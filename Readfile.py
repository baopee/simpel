# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 08:54:41 2018

Subroutine for reading experimental time traces, provided as Bruker file
format.

@author: Stephan Rein, University of Freiburg, 2017
"""

import numpy as np


def read_Elexsys_File(Input, filename=None):
    """read_Elexsys_File()

    in:  Input:                       (data vectors, read from the .DTA binary)
         filename                     (file name of the data file)

    out: pc_spectrum                  (real part of the PELDOR signal)
         pc_imag                      (imaginary part of the PELDOR signal)
         time                         (time vector of the PELDOR signal)

    The function takes the data vectors from the .DTA binary file and uses
    the information given in the description file (.DSC) to construct the
    PELDOR data vectors.
    """
    complexsignal = True
    if filename.endswith('.DTA'):
        filename = filename[0:len(filename)-4]
        filename = filename+".DSC"
        try:
            f = open(filename, 'r')
            t = f.readlines()
            for l in t:
                if l.startswith('IKKF'):
                    s = l.split()
                    if s[1] == 'CPLX':
                        complexsignal = True
                    else:
                        complexsignal = False
                    continue
                if l.startswith('XPTS'):
                    s = l.split()
                    npoints = int(s[1])
                    continue
                if l.startswith('XMIN'):
                    s = l.split()
                    start = float(s[1])
                    continue
                if l.startswith('XWID'):
                    s = l.split()
                    timescale = float(s[1])
                    continue
            pc_spectrum = Input[0:len(Input):2]
            if complexsignal:
                pc_imag = Input[1:len(Input):2]
            elif not complexsignal:
                pc_imag = np.zeros(len(pc_spectrum))
                pc_imag = pc_imag+1e-8
            pc_imag = pc_imag/max(pc_spectrum)
            pc_spectrum = pc_spectrum/max(pc_spectrum)
            pc_imag = pc_imag+1e-8
            stepsize = (timescale)/(npoints-1)
            time = np.arange(npoints)
            time = time*stepsize
            time = time+start
            return pc_spectrum, pc_imag, time
        except:
            print("No .DSC file available")
            pass
    return
