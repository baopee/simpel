#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 17:41:18 2018

@author: spatz
"""

import numpy as np

def initialize(self):
    #Default time trace parameters (distances, coefficients std deviation)
    self.inputvalues = np.zeros(11)
    self.inputvalues[0] = 2
    self.inputvalues[2] = 2
    self.inputvalues[4] = 2
    self.inputvalues[6] = 2
    self.inputvalues[8] = 2
    self.inputvalues[10] = 0.1
    self.inputvalues[1] = 1     
    self.sigmas = np.zeros(5)        
    self.sigmas[0] = 0.1
    self.sigmas[1] = 0.1
    self.sigmas[2] = 0.1
    self.sigmas[3] = 0.1        
    self.sigmas[4] = 0.1     
    self.uni_sigma = 0.1    
    
    #Simulatuon settings (modulation depth, background ...)
    self.moddepth = np.zeros(1)
    self.moddepth[0] = 0.2   
    self.bg_decay = np.zeros(1)
    self.bg_decay[0] = 1
    self.bg_dim = 3
    self.bg_on = 1
    self.showbg = 0
    self.time_bg = np.zeros(1)
    self.timescale = 1500.0
    self.stepsize = 8.0
    self.time = np.zeros(1)
    self.time[0] = 1000
    self.SNRratio  =20
    self.noislevel = 0
    self.noise_on = 0
    self.noisefunction = 0       
    
    #Other initial settings and array allocations
    self.save_on = False
    self.spc_n = np.zeros(1)
    self.spc_bg_n = np.zeros(1)
    self.spectrum = np.zeros(1)
    self.Frequency_region = np.zeros(1)
    self.Fourier = np.zeros(1)
    self.r = np.zeros(1)
    self.Pr = np.zeros(1)
    self.time_bg = np.zeros(1)
    self.bg_function = np.zeros(1)
    self.detach = 0
    self.integrator = 3
    self.superadap = False
    self.warning = False
    self.r_usr = None
    self.Pr_usr = None
    self.userdef = False
    self.TT_usr = None
    self.time_usr = None
    self.TT_userdef = False