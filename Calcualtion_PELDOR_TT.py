# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 17:20:25 2016

@author: Stephan Rein

5 discretized gaussians (23 + x steps or more for large standard deviations) 
are used to approximate a distance distribution. After transformation
into frequency space the integrals are calculated with
full adaption or with a (semiadaptive) trapezoidal grid

function spectrum = Calculate_time_trace(frequencies,time,moddepth,trapezoidal):

-spectrum: Calculated PELDOR time trace

-frequencies: input array with distances and coefficents and modulation depth

-moddepth: input numerical for modulation depth

-trapezoidal: input boolean: false (0) for adaptive integration, true (1)
for composite trapezoidal rule integration

(c) Stephan Rein, University of Freiburg
"""

"""Calculation of PELDOR time traces"""
#from numba import jit
import math as math
import numpy as np
import scipy.integrate as integrate
from scipy.special import fresnel
import random as rand

def calculate_time_trace(frequencies,time,moddepth,trapezoidal,superadap,Jarasbutton):        
    
    """Define coefficients and frequencies as positive"""
    frequencies= np.absolute(frequencies)
    """Get the standard deviation""" 
    sigma = frequencies[10]
    frequencies = np.delete(frequencies,10)    
    freq = frequencies[0::2]
    """Normalize all coefficients"""    
    coef = frequencies[1::2]
    coef = coef/np.sum(coef)
    
    """Define number of theta grid for semid-adpative grid"""         
    numint = 51+int(round(30*(sigma*5)))+int(round(max(time)/100))    

    """Allocation of arrays and numerics""" 
    spectrum = np.zeros(len(time))
    phi = np.zeros(numint)
    fun = np.zeros((len(time),numint))   
    Integration = np.zeros((5,len(time)))
    disttot = 0
    
    for x in range(0,numint):
        phi[x] = (x*math.pi)/(2*numint-2)     
     
    """Define number of theta grid for dpative gaussians""" 
    gaussiansteps =  12+int(round(sigma*80))
    
    """Check if superadaption is switched on"""
    if superadap == True:
        gaussiansteps = gaussiansteps*2
    
    if gaussiansteps%2 == 0:
        gaussiansteps = gaussiansteps+1
    
    
    """Allocate Gaussian function in Freq Space"""
    Gaussian = np.zeros((5))
    Frequencies_to_Gaussian = np.zeros((5,31))
    
    """Define singular array for adaptive integration"""
    tmp_var = np.zeros(0)

    """Main Integration"""
    if trapezoidal == 1:
        print('\nIntegration method:')
        print('\nComposite trapezoidal rule integration\n')                      
        """Loop about the discretized Gaussians"""   
        for number_of_freq in range(0,5): 
            Jarasbutton.setValue(int((number_of_freq+1)*(20)))
            for gstep in range(0,gaussiansteps ):           
                x = (freq[number_of_freq]+3.0*sigma-
                (3.0*sigma*(gstep-1.0))/((gaussiansteps-1.0)/2.0))
    
                Gaussian[number_of_freq] = ((1.0/(math.sqrt(2.0*math.pi*sigma))*
                math.exp(-0.5*(np.power((freq[number_of_freq]-x),2)/(sigma*sigma))))) 
                """Transformation to frequency space"""                    
                frtmp = (327.0/(np.power(x,3)))                                    
                
                Frequencies_to_Gaussian[number_of_freq] = frtmp
                for t in range(0,len(time)):                   
                                        
                    """Trapezoidal integration"""
                    for y in range(0,numint):
                        fun[t,y] = (coef[number_of_freq]*(math.cos((3*(math.cos(phi[y])**2)-1)*frtmp*
                        (time[t]/1000.0))*math.sin(phi[y])))
                        
                Integration[number_of_freq] = integrate.trapz(fun)        
                """Summation over five distances"""    
                spectrum =(spectrum+Gaussian[number_of_freq]*
                Integration[number_of_freq]*moddepth)
                disttot = disttot+(1.0/5.0)*(Gaussian[number_of_freq])            
        spectrum = moddepth*(spectrum/max(spectrum))
    elif trapezoidal == 0:
        print('\nIntegration method:')
        print('\nAdaptive integration\n')           
        """Loop about the discretized Gaussians"""           
        for number_of_freq in range(0,5):
            Jarasbutton.setValue(int((number_of_freq+1)*(20)))
            for gstep in range(0,gaussiansteps ):
                x = (freq[number_of_freq]+3.0*sigma-
                (3.0*sigma*(gstep-1.0))/((gaussiansteps-1.0)/2.0))
    
                Gaussian[number_of_freq] = (1.0/(math.sqrt(2.0*math.pi*sigma))*
                math.exp(-0.5*(np.power((freq[number_of_freq]-x),2)/(sigma*sigma))))           
                
                """Transformation to frequency space"""
                frtmp = (327.0/(np.power(x,3)))               
                
                Frequencies_to_Gaussian[number_of_freq] = frtmp
                for t in range(0,len(time)):                 
                    
                    """Adaptive integration"""
                    function = lambda phi: (coef[number_of_freq]*(math.cos((3*(math.cos(phi)**2)-1)*frtmp*
                    (time[t]/1000.0))*math.sin(phi)))
                    tmp_var = integrate.quad(function,0,math.pi/2, epsabs=1.0e-05)  
                    Integration[number_of_freq,t] = tmp_var[0]

                """Summation over five distances"""
                spectrum =(spectrum+Gaussian[number_of_freq]*
                Integration[number_of_freq,:]*moddepth)
                disttot = disttot+(1.0/5.0)*(Gaussian[number_of_freq]) 

        spectrum = spectrum/(disttot)
       
    elif trapezoidal == 2:
         """Full double integral calculation"""
         print('\nIntegration method:')
         print('\nFully double integral calculation\n')
         for number_of_freq in range(0,5):
             Jarasbutton.setValue(int((number_of_freq+1)*(20)))
             for t in range(0,len(time)): 
                 frtmp_0 = freq[number_of_freq]
                 up_lim = freq[number_of_freq]+3*sigma
                 down_lim = freq[number_of_freq]-3*sigma
                 options={'epsabs':5.0e-04,'limit':20}
                 def function(phi, frtmp):
                     return (coef[number_of_freq]*(math.exp(-0.5*np.power((frtmp_0-frtmp),2)/(sigma*sigma))*
                     (math.cos((3*(math.cos(phi)**2)-1)*(327.0/(np.power(frtmp,3)))*
                     (time[t]/1000.0))*math.sin(phi))))
                 tmp_var = integrate.nquad(function,[[0, (math.pi/2)],[down_lim, up_lim]],opts = [options,options])
                 spectrum[t]  = spectrum[t]+tmp_var[0]  
                     
         spectrum = moddepth*spectrum/max(spectrum)   
         
    elif trapezoidal == 3:
        print('\nIntegration method:')
        print('\nFresnel Type integration\n')           
        """Loop about the discretized Gaussians"""           
        for number_of_freq in range(0,5):
            Jarasbutton.setValue(int((number_of_freq+1)*(20)))
            if coef[number_of_freq] != 0:
                for gstep in range(0,gaussiansteps ):
                    x = (freq[number_of_freq]+3.0*sigma-
                    (3.0*sigma*(gstep-1.0))/((gaussiansteps-1.0)/2.0))
    
                    Gaussian[number_of_freq] = (1.0/(math.sqrt(2.0*math.pi*sigma))*
                    math.exp(-0.5*(np.power((freq[number_of_freq]-x),2)/(sigma*sigma))))           
                
                    """Transformation to frequency space"""
                    frtmp = (327.0/(np.power(x,3)))               
                
                    Frequencies_to_Gaussian[number_of_freq] = frtmp
                    for t in range(0,len(time)):                 
                    
                        a = frtmp*(abs(time[t]/1000.0))
                        tmp = np.zeros(2)
                        if time[t] != 0:
                            b1 = math.sqrt((6/math.pi))*math.sqrt(a)
                            b2 =  math.sqrt(math.pi/6)/(math.sqrt(a))
                            tmp =   fresnel(b1)
                            Integration[number_of_freq][t] =(math.cos(a)*tmp[1]+math.sin(a)*tmp[0])*b2*coef[number_of_freq]
                        else:
                            Integration[number_of_freq][t] = 1.0*coef[number_of_freq]

                    """Summation over five distances"""
                    spectrum =(spectrum+Gaussian[number_of_freq]*
                    Integration[number_of_freq,:]*moddepth)
                    

    spectrum = (spectrum*moddepth)/max(spectrum)
                 
    """"Fourier Analysis"""
    #Fourier = np.zeros(10000)
    stepsize = abs(time[0]-time[1])
    spectrumtmp = spectrum/max(spectrum)
    Fourierim = np.fft.fft(spectrumtmp,10000)
    Frequency_region = np.fft.fftfreq(len(Fourierim),stepsize*0.001)
    Fourierim  = np.fft.fftshift(Fourierim)
    Frequency_region  =np.fft.fftshift(Frequency_region)
    Fourier = np.absolute(Fourierim)
    Fourier = Fourier/max(Fourier)

    stepsize = abs(time[0]-time[1])

    return spectrum,Fourier,Frequency_region
   
   
   
def add_background(spectrum,time,bg_dim,bg_decay,moddepth): 
    """Allocation of vectors"""
    spectrum_with_background = np.zeros((len(time)))    
    background_decay = np.zeros((len(time))) 
    
    bg_dim   = bg_dim/3.0 
    
    """Addition of background"""    
    spectrum_with_background = ((spectrum+1-moddepth)*
    np.exp(-np.power(np.absolute(time),(bg_dim))*bg_decay*0.0001)*moddepth)
    
    """Set up the background function for return"""    
    background_decay = ((1-moddepth)*
    np.exp(-np.power(np.absolute(time),(bg_dim))*bg_decay*0.0001)*moddepth)
    
    return (spectrum_with_background, background_decay)
    
    
    
def add_noise(spectrum,noiselevel): 
    """Allocation of vectors"""   
    spectrum_with_noise = np.zeros((len(spectrum)))    
    noisefunction = np.zeros((len(spectrum)))  

    for i in range(0,len(spectrum)):
        noisefunction[i] = noiselevel*rand.uniform(-1, 1)

    spectrum_with_noise = spectrum+noisefunction
    
    return (spectrum_with_noise, noisefunction)
    
    
    
def calculate_time(timescale, stepsize):
    """Calculate the timescale"""     
    time = np.zeros(1)
    time[0] = -192.0
    x =-192
    y = 1
    while x < timescale:
        time =  np.append(time, stepsize*y-192.0) 
        x = x+stepsize
        y = y+1
              
    return time
    
    
def calculate_distance_distr(frequencies):    
    """Define coefficients and frequencies as positive"""
    frequencies= np.absolute(frequencies)
    """Get the standard deviation""" 
    sigma = frequencies[10]
    frequencies = np.delete(frequencies,10)    
    freq = frequencies[0::2]
    """Normalize all coefficients"""    
    coef = frequencies[1::2]
    coef = coef/np.sum(coef)
    Pr = np.zeros(200)
    r = np.zeros(200)
    Dist_tmp  = np.zeros(1)
    
    for fr in range(0,5):
        for x in range(0,200):
            r[x] = 1.5+(x-1.0)/30.0
            Dist_tmp[0]= coef[fr]*np.exp(-0.5*(np.power((freq[fr]-r[x])/sigma,2)))
            Pr[x] = Pr[x]+Dist_tmp[0]
            
    return (Pr,r)        
    
    