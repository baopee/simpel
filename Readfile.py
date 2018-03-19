# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 08:54:41 2018

@author: stephan
"""

import numpy as np

def read_Elexsys_File(Input,filename = None):
    """Default setting for complex signal"""
    complexsignal = True
    
    if filename.endswith('.DTA') :            
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
                

            pc_spetrum1 = Input[0:len(Input):2]
            if complexsignal == True:
                 pc_imag1 = Input[1:len(Input):2]
            elif complexsignal == False:
                 pc_imag1 = np.zeros(len(pc_spetrum1)) 
                 pc_imag1 = pc_imag1 +0.000001
            pc_imag1 = pc_imag1/max(pc_spetrum1)
            pc_spetrum1 = pc_spetrum1/max(pc_spetrum1)
            pc_imag1 = pc_imag1+0.000001
            stepsize = (timescale)/(npoints-1)
            time1 =  np.arange(npoints)
            time1 = time1*stepsize
            time1  = time1 +start                   
            return pc_spetrum1, pc_imag1, time1
        except:
            print("No .DSC file available")
            pass
    return