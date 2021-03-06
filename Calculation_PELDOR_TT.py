# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 17:20:25 2016

@author: Stephan Rein

Simulation kernel for PELDOR/DEER data

The program is distributed under a 2-clause license
("Simplified BSD License" or "FreeBSD License")
For further details see LICENSE.txt

Copyright (c) 2018, Stephan Rein
All rights reserved.
"""

# External libraries
import numpy as np
from scipy.special import fresnel


def calculate_time_trace(frequencies, time, moddepth, trapezoidal, superadap,
                         Jarasbutton, sigmas, userdef, r_usr=None,
                         Pr_usr=None):
    """"

    in:  frequencies        (vector with central distances, given as frequency)
         time               (time vector)
         moddepth           (overall modulation depth)
         trapezoidal        (integration method)
         superadap          (if True then use higher discretization rate)
         Jarasbutton        (object for the progress button)
         sigmas             (vector with standard deviations)
         userdef            (if True use a user defined dist. distribution)
         r_usr              (user defined distance vector)
         Pr_usr             (user defined distance distribution)

    out: spectrum           (PELDOR time trace)
         Fourier            (Fourier transform of the PELDOR time trace)
         Frequency_region   (x-axis of the Fourier transf. of the time trace)
         warning            (warning flag for short distances)

    The function converts the user defined information into a PELDOR time
    trace. Either a Gaussian model is used with up to 5 Gaussian functions,
    or a user-defined distance distribution is passed
    (loaded from a .txt file). The function takes the input and passes all
    information to either the internal_PELDOR_kernel() function or the
    PELDOR_matrix_kernel() function.
    """
    if userdef:
        spectrum = PELDOR_matrix_kernel(r_usr, Pr_usr, time, moddepth)
        warning = False
    else:
        frequencies = np.absolute(frequencies)
        frequencies = np.delete(frequencies, 10)
        freq = frequencies[0::2]
        coef = frequencies[1::2]
        coef = coef/np.sum(coef)
        sigma = max(sigmas)
        spectrum = np.zeros(len(time))
        gaussiansteps = 19+int(round(sigma*100))
        if superadap:
            gaussiansteps = gaussiansteps*3
        if trapezoidal == 2:
            gaussiansteps = gaussiansteps*5
        if gaussiansteps % 2 == 0:
            gaussiansteps = gaussiansteps+1
        warning = False
        # Check warning
        x_g = np.zeros((5, gaussiansteps))
        for number_of_freq in range(0, 5):
            for gstep in range(0, gaussiansteps):
                x_g[number_of_freq, gstep] = (freq[number_of_freq] +
                                              3.0*sigmas[number_of_freq] -
                                              (3.0*sigmas[number_of_freq] *
                                              (gstep-1.0)) /
                                              ((gaussiansteps-1.0)/2.0))
                if x_g[number_of_freq, gstep] <= 0:
                    x_g[number_of_freq, gstep] = 1e-8
                    warning = True
        spectrum = internal_PELDOR_kernel(freq, coef, sigmas, moddepth, time,
                                          3, gaussiansteps)
    # Fourier Decomposition
    stepsize = abs(time[0]-time[1])
    spectrumtmp = spectrum/max(spectrum)
    Fourierim = np.fft.fft(spectrumtmp, 10000)
    Frequency_region = np.fft.fftfreq(len(Fourierim), stepsize*0.001)
    Fourierim = np.fft.fftshift(Fourierim)
    Frequency_region = np.fft.fftshift(Frequency_region)
    Fourier = np.absolute(Fourierim)
    Fourier = Fourier/max(Fourier)
    stepsize = abs(time[0]-time[1])
    return spectrum, Fourier, Frequency_region, warning


def internal_PELDOR_kernel(dist, coef, sigma, moddepth, time, num,
                           gaussiansteps):
    """"

    in:  dist               (vector with distances)
         coef               (vector of linear coef. for the Gaussian functions)
         sigma              (standard deviations for the Gaussian functions)
         moddepth           (overall modulation depth)
         time               (time vector)
         num                (numeric value that defines Gaussian eval. range)
         gaussiansteps      (number of discretized Gaussian steps)

    out: signal             (PELDOR signal, normalized to the modulation depth)

    The function converts the user defined information of positions,
    standard deviation, linear coefficients ..... into a PELDOR time trace
    with up to 5 contributing Gaussian functions.
    """
    time = time/1000
    time_tmp_mat = np.ones((len(dist), gaussiansteps, len(time)))
    time_tmp_mat = time_tmp_mat*(np.absolute(time))
    try:
        nozero = True
        indext0 = np.argwhere(np.abs(time) < 1e-6)[0][0]
    except:
        nozero = False
    y = np.zeros((gaussiansteps, len(dist)))
    fr = np.zeros((gaussiansteps, len(dist)))
    ditr = np.zeros((gaussiansteps, len(dist)))
    for gau in range(0, len(dist)):
        y = (np.linspace(dist[gau]-num*sigma[gau], dist[gau] +
             num*sigma[gau], gaussiansteps))
        ditr[:, gau] = np.exp(-0.5*np.power((dist[gau]-y), 2) /
                              (sigma[gau]*sigma[gau]))
        ditr[:, gau] = ditr[:, gau]/np.sum(ditr[:, gau])
        fr[:, gau] = (327.0/np.power(y, 3))
    # Fully vectorized Fresnel integral evaluation
    fi = np.transpose(np.abs(fr)*np.transpose(time_tmp_mat))
    b1 = np.sqrt(6/np.pi)*np.sqrt(fi)
    tmpfresnel = fresnel(b1)
    if nozero:
        b1[:, :, indext0] = 1.0
    integral = np.transpose((np.cos(fi)*tmpfresnel[1]+np.sin(fi) *
                            tmpfresnel[0])/(b1))*coef
    if nozero:
        integral[indext0, :, :] = coef
    signal = np.sum(np.sum((ditr*(integral)), axis=2), axis=1)
    if max(signal) < 1e-20:
        signal += 1e-8
    return (moddepth*(signal/max(signal)))


def PELDOR_matrix_kernel(r_usr, Pr_usr, time, moddepth):
    """"

    in:  time: (1xn) time vector in ns units
         r_usr: (1xm) user defined distance vector
         Pr_usr: (1xm) distance distribution vector

    out: signal: (1xn) PELDOR signal, normalized to the modulation depth

    The function takes a user defined ditance distribution (Pr_user) to
    create a corresponding PELDOR time trace.
    """
    time = time/1000.0
    kernel = np.zeros((len(time), len(Pr_usr)))
    indext0 = np.argwhere(np.abs(time) < 1e-6)[0][0]
    for i in range(0, len(r_usr)):
        w = (327.0/(np.power(r_usr[i], 3)))
        z = np.sqrt((6*w*np.absolute(time))/np.pi)
        tmpfresnel = fresnel(z)
        kernel[indext0, :] = 1.0
        z[indext0] = 1
        kernel[:, i] = ((np.cos(w*np.absolute(time))/z)*tmpfresnel[1] +
                        (np.sin(w*np.absolute(time))/z)*tmpfresnel[0])
    kernel[indext0][:] = 1.0
    signal = kernel@Pr_usr
    return (moddepth*(signal/max(signal)))


def add_background(spectrum, time, bg_dim, bg_decay, moddepth):
    """

    in:  spectrum               (PELDOR time trace without background function)
         time                   (time vector)
         bg_dim                 (background dimension 1<= bg_dim <= 6)
         bg_decay               (exponential decay constant)
         moddepth               (overall modulation depth)

    out: spectrum_with_background  (PELDOR time trace with background function)
         background_decay          (Background function)

    The function adds a background function to the PELDOR time trace. The
    background function is supposed to be a streched exponential decay.
    """
    spectrum_with_background = np.zeros((len(time)))
    background_decay = np.zeros((len(time)))
    bg_dim = bg_dim/3.0
    spectrum_with_background = ((spectrum+1-moddepth) *
                                np.exp(-np.power(np.absolute(time), (bg_dim)) *
                                bg_decay*0.0001)*moddepth)
    background_decay = ((1-moddepth) *
                        np.exp(-np.power(np.absolute(time), (bg_dim)) *
                        bg_decay*0.0001)*moddepth)
    return (spectrum_with_background, background_decay)


def add_noise(spectrum, noiselevel):
    """

    in:  spectrum                          (PELDOR time trace without noise)
         noiselevel                        (level of the signal-to-noise ratio)

    out: spectrum_with_noise               (PELDOR time trace with noise)
         noisefunction                     (function with additive noise)

    The function adds white noise to an existing PELDOR time trace.
    """
    spectrum_with_noise = np.zeros((len(spectrum)))
    noisefunction = np.zeros((len(spectrum)))
    for i in range(0, len(spectrum)):
        noisefunction[i] = np.random.normal(0, noiselevel)
    spectrum_with_noise = spectrum+noisefunction
    return (spectrum_with_noise, noisefunction)


def calculate_time(timescale, stepsize, t_min):
    time = np.arange(t_min, timescale+stepsize, stepsize)
    return time


def calculate_distance_distr(frequencies, sigmas, configs):
    frequencies = np.absolute(frequencies)
    frequencies = np.delete(frequencies, 10)
    freq = frequencies[0::2]
    coef = frequencies[1::2]
    coef = coef/np.sum(coef)
    configs["points"] = int(configs["points"])
    Pr = np.zeros(configs["points"])
    r = np.linspace(configs["r_min"], configs["r_max"], configs["points"],
                    endpoint=True)
    for fr in range(0, 5):
        Pr += (coef[fr]*(1.0/(np.sqrt(2.0*np.pi)*sigmas[fr])) *
               np.exp(-0.5*(np.power((freq[fr]-r)/sigmas[fr], 2))))
    return (Pr, r)
