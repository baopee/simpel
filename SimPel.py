"""
@author: Stephan Rein

SIMPEL 2018 is a Python3/PyQt5 based GUI application for the fast and efficient
simulation of PELDOR/DEER data.


The program is distributed under a 2-clause license 
("Simplified BSD License" or "FreeBSD License")
For further details see LICENSE.txt

Copyright (c) 2018, Stephan Rein

"""


#Import external libraries
import numpy as np
import datetime
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QVBoxLayout,QFileDialog,QSplashScreen, QDialog)
from PyQt5.QtGui import  QPixmap,QIcon
import matplotlib
matplotlib.use("Qt5Agg",force=True)
import time, sys, os
#Import internal subfunctions
import SimPel_Layout 
from Calculation_PELDOR_TT import (calculate_time_trace,add_background,add_noise)
from Calculation_PELDOR_TT import calculate_time, calculate_distance_distr
from Initialize import initialize
from Readfile import read_Elexsys_File
from SimPel_config_GUI import Ui_Configurations_Dialog as ChildConfig
import copy as copy
import warnings as warnings
warnings.filterwarnings("ignore")



#Default configurations
configs = {"r_min":1.2,"r_max":8,"sigma_max":1.1,"sigma_min":0.0,
           "axeslabelfontsize": 9,"fontsize":10,"xmargin": 0.0,"ymargin": 0.1,
           "xsize":4,"ysize":3,"points":881,"linewidth":1.5,"t_min":-200}

configs_str = {"ylabel_time_trace":r'$Intensity$', 
           "xlabel_time_trace" : r"$time\ \mathrm{/ \ ns}$","ylabel_dd":r'$Normalised\ \ Intensity$',
           "xlabel_dd" :r'$r\ \mathrm{/ \ nm}$',"autosave":"True","figure_format": 'png,pdf',
           "yticks_time_trace": "True", "yticks_dd": "False","title_time_trace":"True","title_dd":"True",
           "colorL": "blue","colorBG": "red","showuserTT":"True","ColorUser":"grey"}

configs_lim_min = {"r_min":0.5,"sigma_min":0.0,"t_min":-2000,
           "axeslabelfontsize": 2,"fontsize":2,"xmargin": -0.5,
           "ymargin": -0.5,"xsize":1,"ysize":1,"linewidth":0.5}

configs_lim_max = {"r_max":16,"sigma_max":1.1,
           "xmargin": 0.5, "ymargin": 0.8,"xsize":100,"ysize":100,"linewidth":10,"t_min":0}

config_filename = "SimPel.conf"

try:
    f = open(config_filename, 'r')
    t = f.readlines()
    for l in t:
        for key in configs:
            if key in l:
                s = l.split("=")
                s = s
                try:
                    configs[key] = float(s[1])
                    if key in configs_lim_min.keys():
                        if configs[key] < configs_lim_min[key]:
                            configs[key] = configs_lim_min[key]
                    if key in configs_lim_max.keys():
                        if configs[key] > configs_lim_max[key]:
                            configs[key] = configs_lim_max[key]                    
                except: 
                    pass                    
    f.close()
except:
    pass

try:
    f = open(config_filename, 'r')
    t = f.readlines()
    for l in t:
        for key in configs_str:
            k = l.split("=")
            if key in l:
                s = l.split("=")
                s = s    
                try:
                   s[1] = s[1].rstrip()    
                   s[1] = s[1].lstrip() 
                   configs_str[key] = s[1]
                except: 
                    pass                    
    f.close()
except:
    pass

# Adjust the font-size to the current matplotlib-version
try:
    mat_version =repr(matplotlib.__version__)
    mat_version_str=(eval(mat_version))
    num_ver = (mat_version_str).split('.')
    if int(num_ver[0]) == 2:
        configs["fontsize"] = 8
        configs["axeslabelfontsize"]  = 7       
    else:    
        configs["fontsize"] = 10
        configs["axeslabelfontsize"]  = 9       
except:
    configs["fontsize"] = 9
    configs["axeslabelfontsize"]  = 8  




#Define relative path (even when temporary in _MEIPASS)
def resource_path(relative_path):
    try:
        return os.path.join(sys._MEIPASS, relative_path)
    except Exception:
        return os.path.join(os.path.abspath("."),relative_path)
    except:
        return relative_path  




#GUI Main Class for SimPel2018
class SimPelDesign(QMainWindow,SimPel_Layout.Ui_SimPel2018):
    def __init__(self):        
        
        # Inheritage from the base/super class
        super(self.__class__, self).__init__()
        self.setupUi(self)  
        self.icon2 = QIcon()
        self.icon2.addPixmap(QPixmap(resource_path("SimPel_icon.ico")))
        self.setWindowIcon(self.icon2)
        self.versionnumber  = '1.0.0'              
        #customized QWidgets as containing matplotlib figure instances
        self.figure = Figure()
        self.figure.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)        
        self.layout= QVBoxLayout(self.widgetplot)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)  
        self.ax.set_yticks([]) 
        self.ax.set_xticks([])  
        self.figure2 = Figure()
        self.figure2.set_facecolor('white')
        self.canvas2 = FigureCanvas(self.figure2)        
        self.layout2 =  QVBoxLayout(self.Distancedistrwindow)
        self.layout2.addWidget(self.canvas2)
        self.ax2 = self.figure2.add_subplot(111)  
        self.ax2.set_yticks([]) 
        self.ax2.set_xticks([])          
        self.figure3 = Figure()
        self.figure3.set_facecolor('white')
        self.canvas3 = FigureCanvas(self.figure3)        
        self.layout3 = QVBoxLayout(self.FTwindow)
        self.layout3.addWidget(self.canvas3)
        self.ax3 = self.figure3.add_subplot(111)  
        self.ax3.set_yticks([]) 
        self.ax3.set_xticks([])          
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()  
                 
        #Initialize all parameters         
        initialize(self)
        self.configs = configs
        self.configs_str = configs_str
        self.configs_lim_min = configs_lim_min
        self.configs_lim_max = configs_lim_max
        
        #ALL SIGNAL/SLOT CONNECTIONS         
        self.Startbutton.clicked.connect(self.make_calculation) 
        self.zoomButtonPeldorTT.clicked.connect(self.zoominPELDORTT)   
        self.panPELDORTT.clicked.connect(self.makepanPELDORTT)
        self.DetachButton.clicked.connect(self.makeDetachfigure) 
        
        self.Distance1edit.textChanged.connect(lambda:self.read_dist(self.Distance1edit.text(),0))
        self.Distance2edit.textChanged.connect(lambda:self.read_dist(self.Distance2edit.text(),1))
        self.Distance3edit.textChanged.connect(lambda:self.read_dist(self.Distance3edit.text(),2))
        self.Distance4edit.textChanged.connect(lambda:self.read_dist(self.Distance4edit.text(),3))
        self.Distance5edit.textChanged.connect(lambda:self.read_dist(self.Distance5edit.text(),4))        
        
        self.Coeff1edit.textChanged.connect(lambda:self.read_coeff(self.Coeff1edit.text(),0))
        self.Coeff2edit.textChanged.connect(lambda:self.read_coeff(self.Coeff2edit.text(),1))
        self.Coeff3edit.textChanged.connect(lambda:self.read_coeff(self.Coeff3edit.text(),2))
        self.Coeff4edit.textChanged.connect(lambda:self.read_coeff(self.Coeff4edit.text(),3))        
        self.Coeff5edit.textChanged.connect(lambda:self.read_coeff(self.Coeff5edit.text(),4))
        
        self.Standard1.textChanged.connect(lambda:self.read_sigmas(self.Standard1.text(),0))
        self.Standard2.textChanged.connect(lambda:self.read_sigmas(self.Standard2.text(),1))
        self.Standard3.textChanged.connect(lambda:self.read_sigmas(self.Standard3.text(),2))
        self.Standard4.textChanged.connect(lambda:self.read_sigmas(self.Standard4.text(),3))
        self.Standard5.textChanged.connect(lambda:self.read_sigmas(self.Standard5.text(),4))        
        
        self.Timescalebox.valueChanged.connect(self.set_stepsize)
        self.Timescalebox.lineEdit().setReadOnly(True)
        self.Timescaleedit.textChanged.connect(self.read_timescale)        
        self.Moddepthedit.textChanged.connect(self.read_moddpeth)
        
        self.Bgdecayedit.textChanged.connect(self.read_bgdecy)
        self.BgDimbox.valueChanged.connect(self.set_bgdim)
        self.BgDimbox.lineEdit().setReadOnly(True)
        self.EnableBgButton.toggled.connect(lambda:self.btn1state(self.EnableBgButton))
        self.ShowBGButton.toggled.connect(lambda:self.btn2state(self.ShowBGButton))        
        self.Sigmaedit.textChanged.connect(self.read_sigma)   
        self.Universal_standard_dev_button.toggled.connect(lambda:self.use_universal_sigma(self.Universal_standard_dev_button))        
        self.EnableNoiseButton.toggled.connect(lambda:self.btn3state(self.EnableNoiseButton))
        self.SNR_edit.textChanged.connect(self.read_SNR)            
        self.Checkbox_superadaptive.stateChanged.connect(lambda:self.use_superadaptive_Gaussian(self.Checkbox_superadaptive))
        self.ButtonFullyAdaptive.toggled.connect(lambda:self.btn5state(self.ButtonFullyAdaptive))
        self.fresnelbutton.toggled.connect(lambda:self.btn7state(self.fresnelbutton))
        self.User_defined_distr.toggled.connect(lambda:self.Userdef_Dist(self.User_defined_distr))

        self.Load_experimental_button.clicked.connect(self.open_file_TT)
        self.Configurations.clicked.connect(self.open_config)
        self.Loadbutton_User_def.clicked.connect(self.open_file)
        self.Savebutton.clicked.connect(self.save_file)
        self.Closebutton.clicked.connect(self.close_GUI)  



    #MEMBER FUNCTIONS OF SIMPEL2018
    def open_file(self, t):
        self.dialog = QFileDialog()
        name, name_tmp = self.dialog.getOpenFileName(self, 'Open File',None,"*.txt (*.txt *.TXT)")  
        if not name:
            return
        if name.endswith('.txt') or name.endswith('.TXT') :
            try:        
                k = np.loadtxt(name)
                try:
                    k1, k2 = np.transpose(k)
                except:
                    k1, k2 = k
                ind = name.rfind("/")
                if ind == -1:
                    self.filename = name
                else:
                    self.filename =  name[ind+1:]
                if min(k1) <= 0 or max(k1) > 10 or min(k2) <-0: 
                    self.War3 = QMessageBox.warning(self,"Corrupted data",
                            "Weird distance distribution. Simulation won't be carried out!",QMessageBox.Ok)                               
                else: 
                    self.r_usr = k1
                    self.Pr_usr = k2
                    self.Label_user_def_dist.setText(str(self.filename))
            except:
                self.War4 = QMessageBox.warning(self,"Import Error",
                "Something went wrong! Data could not be loaded. ",QMessageBox.Ok)
        return
        
        
        
    #MEMBER FUNCTIONS OF SIMPEL2018
    def open_file_TT(self, t):
        self.dialog = QFileDialog()
        name, name_tmp = self.dialog.getOpenFileName(self, 'Open File',None,"*.txt (*.txt *.TXT);;*dta (*.DTA *.dta)")  
        if not name:
            return
        if name.endswith('.txt') or name.endswith('.TXT') :
            try:        
                k = np.loadtxt(name)
                try:
                    k1, k2 = np.transpose(k)
                except:
                    k1, k2 = k
                ind = name.rfind("/")
                if ind == -1:
                    self.filename = name
                else:
                    self.filename =  name[ind+1:]
                if min(k1) <= -500 or max(k1) > 1000000000: 
                    self.War3 = QMessageBox.warning(self,"Corrupted data",
                            "Weird PELDOR trace. Cannot be plotted!",QMessageBox.Ok)                               
                else: 
                    self.time_usr = k1
                    self.TT_usr = k2
                    self.TT_userdef = True
                    try:
                        self.make_calculation()
                    except:
                        pass
            except:
                self.War4 = QMessageBox.warning(self,"Import Error",
                "Something went wrong! Data could not be loaded. ",QMessageBox.Ok)
        elif name.endswith('.DTA') or name.endswith('.dta') :
            try:
                f = open(name, 'rb') 
                data_type = np.dtype('>f8')
                Input = np.fromfile(f, data_type)  
                self.TT_usr, self.imag, self.time_usr= read_Elexsys_File(Input,name)    
                self.make_calculation()
                self.TT_userdef = True
                try:
                    self.make_calculation()
                except:
                    pass
            except:
                self.War4 = QMessageBox.warning(self,"Import Error",
                "Something went wrong! Data could not be loaded. ",QMessageBox.Ok)                
        return                



    def Userdef_Dist(self,integr):
        if self.User_defined_distr.isChecked() == True:
            if self.Pr_usr is None:
                self.War2 = QMessageBox.warning(self,"No file loaded.",
                            "No distance distribution loaded yet!",QMessageBox.Ok)                                                            
                self.fresnelbutton.setChecked(True)
        return    
            


       
    def make_calculation(self):      
        #Enable the possibility to save the ouput
        self.save_on = True   
        if self.User_defined_distr.isChecked() == True:
            self.userdef = True
        else:
            self.userdef = False
        if self.Universal_standard_dev_button.isChecked() == True:
            self.Standard1.setText(str(self.uni_sigma))
            self.Standard2.setText(str(self.uni_sigma))
            self.Standard3.setText(str(self.uni_sigma))
            self.Standard4.setText(str(self.uni_sigma))
            self.Standard5.setText(str(self.uni_sigma))             
        #Simulation kernel functions are called for PELDOR time trace calculation  
        self.Pr,self.r = calculate_distance_distr(self.inputvalues,self.sigmas,self.configs)
        self.JarasprogressBar.setValue(0)
        QApplication.processEvents()
        self.time = calculate_time(self.timescale,self.stepsize,self.configs["t_min"])
        self.spectrum,self.Fourier,self.Frequency_region, self.warning = calculate_time_trace(self.inputvalues,
                                        self.time,self.moddepth,self.integrator,
                                        self.superadap,self.JarasprogressBar, self.sigmas,self.userdef,self.r_usr,self.Pr_usr)                                                                       
        self.JarasprogressBar.setValue(0)
        #Create static values for potential output file
        self.inputvalues_static =  self.inputvalues
        self.sigmas_static =  self.sigmas
        self.timescale_static = self.timescale
        self.stepsize_static = self.stepsize
        self.moddepth_static = self.moddepth
        self.integrator_static =  self.integrator
        self.make_noise()  
        self.make_background()                         
        #Uptade all plots                                            
        self.plot_TT()
        self.plot_DD()
        self.plot_FT()
        if hasattr(self, 'figure4') or  hasattr(self, 'figure5') :   
            self.detach_plot_TT()
        if self.warning    == True:
            self.War = QMessageBox.warning(self,
            "Negative distances.",
            "The given distance distribution has contributions in the negative distance domain.\n\n"+
            "You should reduce the standard deviation or increase the distance!",
                                     QMessageBox.Ok)                                       
            self.warning = False
        self.JarasprogressBar.setValue(int(100))
        QApplication.processEvents()
        return



        
    def make_background(self):
        if self.bg_on == 1:
            self.spc_bg_n,self.bg_function= add_background(self.spc_n,self.time,self.bg_dim,
                                  self.bg_decay,self.moddepth)
        else:
            self.spc_bg_n = self.spc_n               
            self.bg_function = np.zeros(len(self.spc_n))       
        n = 0
        while n < len(self.time):
            if self.time[n] >= 0:
                break
            n = n+1              
        self.time_bg = self.time[n::]
        self.bg_function = self.bg_function[n::] 
        if self.save_on == False:
            return                       
        self.plot_TT()  
        if hasattr(self, 'figure4') or  hasattr(self, 'figure5') :   
            self.detach_plot_TT()
        return



    def make_noise(self):
        if self.noise_on == 1:
            self.noislevel =self.moddepth[0]/self.SNRratio 
            self.spc_n,self.noisefunction= add_noise(self.spectrum,self.noislevel)
        else:
            self.spc_n = self.spectrum
        if self.save_on == False:
            return
        self.make_background()        
        return
        
        
 
    def zoominPELDORTT(self):        
        self.toolbar.zoom()
        
        
        
    def makepanPELDORTT(self):        
        self.toolbar.pan()
        
        
        
    def makeDetachfigure(self):
        if hasattr(self, 'figure4'):   
            pass
        else:
            self.figure4 = Figure()
            self.canvas4 = FigureCanvas(self.figure4)  
            self.ax4 = self.figure4.add_subplot(111)
        if hasattr(self, 'figure5'):   
            pass
        else:            
            self.ax4 = self.figure4.add_subplot(111)
            self.figure5 = Figure()
            self.canvas5 = FigureCanvas(self.figure5)  
            self.ax5 = self.figure5.add_subplot(111)        
        self.detach_plot_TT()
        
        
        
    #Definition of all distances used in the simulation          
    def read_dist(self, text, n): 
        try:
            if float(text) <= self.configs["r_max"] and float(text) >= self.configs["r_min"]:
                self.inputvalues[2*n] = float(text)
            else:
                self.Distance1edit.setText(str(2.0))
                self.inputvalues[2*n] =2.0
        except:    
            self.Distance1edit.setText(str(2.0))            
            self.inputvalues[2*n] = 2.0
           
         
    #Definition of the linear coefficients
    def read_coeff(self,  text, n):  
        try:
            if float(text) <= 1.0 and float(text) >= 0:
                self.inputvalues[2*n+1] = float(text)
            else:
                self.Coeff1edit.setText(str(1.0))
                self.inputvalues[2*n+1] = 1.0
        except:    
            self.Coeff1edit.setText(str(1.0))            
            self.inputvalues[2*n+1] = 1.0

            
            
 
    #Definition of standard deviations  
    def read_sigmas(self, text,n): 
        try:
            if float(text) <= configs["sigma_max"] and float(text) > configs["sigma_min"]:
                self.sigmas[n] = float(text)
            else:
                self.Standard1.setText(str(self.sigmas[n]))
        except:
            val = 0.1
            self.Standard1.setText(str(val))
            self.sigmas[n] = 0.1
            
            
       

    def set_stepsize(self, value): 
        self.stepsize = value          



    def read_timescale(self, ts): 
        try:
            if float(ts) <= 100000.0 and float(ts) >= 0:
                self.timescale = float(ts)
            else:
                self.Timescaleedit.setText(str(1500)) 
                self.timescale = 1500
        except:        
                self.Timescaleedit.setText(str(1500)) 
                self.timescale = 1500           



    def read_moddpeth(self, md): 
        try:
            if float(md) <= 1.0 and float(md) >= 0:
                self.moddepth[0] = float(md)
            else:
                self.Moddepthedit.setText(str(0.2)) 
                self.moddepth[0] = 0.2
        except:
                self.Moddepthedit.setText(str(0.2)) 
                self.moddepth[0] = 0.2
                
        if self.moddepth[0]==0:
            self.moddepth[0] = 0.00001        
        return




    def read_bgdecy(self, dc): 
        try:
            if float(dc) <= 100000.0 and float(dc) >= 0:
                self.bg_decay[0] = float(dc)
            else:
                self.Bgdecayedit.setText(str(1.0))      
                self.bg_decay[0] =1.0
        except:
            self.Bgdecayedit.setText(str(1.0))      
            self.bg_decay[0] =1.0            
        
        self.make_background()   
        return
        
        

    def set_bgdim(self, value_dim): 
        self.bg_dim = value_dim 
        self.make_background()
        return
        



    def btn1state(self,bgenaleb):
        if bgenaleb.isChecked() == True:
            self.bg_on = 1
        else:
            self.bg_on = 0
        self.make_background()    
        return              



    def btn2state(self,bgenaleb):
        if bgenaleb.isChecked() == True:
            self.showbg = 1
        else:
            self.showbg = 0
        if self.save_on == False:
            return
        self.plot_TT()   
        self.detach_plot_TT()
        return    
        

        
    def btn3state(self,noiseenaleb):
        if noiseenaleb.isChecked() == True:
            self.noise_on = 1
        else:
            self.noise_on = 0
        if self.save_on == False:
            return
        self.make_noise()
        return 


    #Use universial standard deviation
    def read_sigma(self,sigval):
        try:
            if float(sigval) <= 1 and float(sigval) > 0:
                self.uni_sigma  = float(sigval)
            else:
                self.uni_sigma  = 0.1
                self.Sigmaedit.setText(str(self.uni_sigma)) 
            if self.uni_sigma <0.001:
                self.uni_sigma  = 0.1                  
                self.Sigmaedit.setText(str(self.uni_sigma)) 
        except:
                self.uni_sigma  = 0.1                  
                self.Sigmaedit.setText(str(self.uni_sigma))                 
        if self.Universal_standard_dev_button.isChecked() == True:
            self.Standard1.setText(str(self.uni_sigma))
            self.Standard2.setText(str(self.uni_sigma))
            self.Standard3.setText(str(self.uni_sigma))
            self.Standard4.setText(str(self.uni_sigma))
            self.Standard5.setText(str(self.uni_sigma))                         
        return



    def use_universal_sigma(self,sigval):
        if self.Universal_standard_dev_button.isChecked() == True:
            self.Standard1.setText(str(self.uni_sigma))
            self.Standard2.setText(str(self.uni_sigma))
            self.Standard3.setText(str(self.uni_sigma))
            self.Standard4.setText(str(self.uni_sigma))
            self.Standard5.setText(str(self.uni_sigma))            
        return



    def read_SNR(self, dc): 
        try:
            if float(dc) <= 100000.0 and float(dc) >= 0:
                self.SNRratio = float(dc)
            else:
                self.SNR_edit.setText(str(20.0))      
                self.SNRratio = 20.0
        except:
                self.SNR_edit.setText(str(20.0))      
                self.SNRratio = 20.0                
        self.make_noise()   
        return
        


    def btn4state(self,integr):
        if integr.isChecked() == True:
            self.integrator = 1
            
        else:
            self.integrator = 3    
        self.userdef = False    
        return 



    def btn5state(self,integr):
        if integr.isChecked() == True:
            self.integrator = 2
            if self.superadap == True:
                self.superadap = False
                self.Checkbox_superadaptive.setCheckState(False)
        else:
            self.integrator = 3   
        self.userdef = False    
        return 
        
        
        
    def btn6state(self,integr):
        if integr.isChecked() == True:
            self.integrator = 0
        else:
            self.integrator = 3   
        self.userdef = False    
        return         



    def btn7state(self,integr):
        if integr.isChecked() == True:
            self.integrator = 3
        else:
            self.integrator = 3  
        self.userdef = False    
        return   



    def use_superadaptive_Gaussian(self,adaptiveon):     
        if (adaptiveon.isChecked() == True and not self.integrator == 2):
            self.superadap = True
        elif(adaptiveon.isChecked() == True and self.integrator == 2): 
            self.superadap = False
            self.Checkbox_superadaptive.setCheckState(False)
        else:
            self.superadap = False



    #Save the current simulation in output files (.txt or .dat file)     
    def save_file(self):
        if self.save_on == False:
            return
        dialog = QFileDialog()
        dialog.setStyleSheet("background-color:rgb(255, 255, 255)")
        save_name, name_tmp= dialog.getSaveFileName(self, 'Save File',None,"*.txt (*.txt);;*dat (*.dat)") 
        if not  save_name:
            return False
        name = str(save_name)              
        if not (name.endswith('.txt') or name.endswith('.dat')) :
            name += '.txt' 
        filetyp = '.txt'
        if '.txt' in name:
            pos = name.index('.txt')
            filetyp = '.txt'
            name = name[0:pos]
        elif '.dat' in name:
            pos = name.index('.dat')
            filetyp = '.dat'
            name = name[0:pos]            
        strTT = '_Time_trace'
        strFT = '_Fourier_transform'
        strDD = '_Distance_distribution'
        strBG = '_Backgound_Function'
        strinfo = '_Information_sheet'    
        #File 1 (time trace)
        tmparra = np.array( np.transpose((self.time,self.spc_bg_n)))    
        y = tmparra.reshape((len(self.time),2))
        with open(name+strTT+filetyp,'w')   as file:
            file.write("\n".join("   ".join(map("{:.8f}".format, x)) for x in (y)))
        file.close() 
        #File 2 (fourier transform of the time trace)
        tmparra = np.array( np.transpose((self.Frequency_region, self.Fourier)))        
        y = tmparra.reshape((len(self.Frequency_region),2))
        with  open(name+strFT+filetyp,'w')    as file:
            file.write("\n".join("   ".join(map("{:.8f}".format, x)) for x in (y)))
        file.close() 
        #File 3 (distance distribution)  
        if self.userdef == False:          
            tmparra = np.array( np.transpose((self.r,self.Pr)))
            y = tmparra.reshape((len(self.r),2))
        else: 
            tmparra = np.array( np.transpose((self.r_usr,self.Pr_usr)))
            y = tmparra.reshape((len(self.r_usr),2))
        with  open(name+strDD+filetyp,'w')    as file:
            file.write("\n".join("   ".join(map("{:.8f}".format, x)) for x in (y)))
        file.close() 
        #File 4 (background function of the time signal)               
        tmparra = np.array(np.transpose((self.time_bg, self.bg_function)))
        y = tmparra.reshape((len(self.time_bg),2))
        with  open(name+strBG+filetyp,'w')    as file:
            file.write("\n".join("   ".join(map("{:.8f}".format, x)) for x in (y)))
        file.close() 
        #File 5 (information file which contains all simulation settings)                
        with open(name+strinfo+filetyp,'w') as file:
            file.write("Infosheet for PELDOR/DEER Simulation. Original Path:\n"+ name+ "\n\n")
            file.write("Simulated with SimPel"+self.versionnumber+"\n\n")           
            file.write("Analyzed at: ")
            now = datetime.datetime.now()
            file.write(now.strftime("%Y-%m-%d %H:%M:%S"))
            file.write("\n\n\n*************Simulation Parameter*****************\n\n" )  
            if self.userdef == False:
                file.write("Distance / nm \t Coefficient\t  sigma / nm\n") 
                for i in range(0,len(self.sigmas)):
                    value = str("%.4f" %  self.inputvalues_static[2*i])
                    file.write(value+ "\t         ")
                    value = str("%.4f" %  self.inputvalues_static[2*i+1])
                    file.write(value+ "\t          ")
                    value = str("%.4f" %  self.sigmas_static[i])
                    file.write(value+ "\t         ")
                    file.write("\n")
            else:
                file.write("Distance distribution were taken from external file: ")
                file.write(str(self.filename))
                file.write("\n")
            boolstr = str(self.EnableNoiseButton.isChecked())        
            file.write("\n\nPELDOR/DEER step size: "+str(self.stepsize_static)+' ns')            
            file.write("\n\nPELDOR/DEER time scale: "+str(self.timescale_static)+' ns')       
            file.write("\n\nPELDOR/DEER modulation depth: "+str(self.moddepth_static[0]))  
            file.write("\n\nGaussian noise enabled: "+boolstr) 
            if self.EnableNoiseButton.isChecked() == True:
                SNRvalue = str("%.3f" %  self.SNRratio)
                file.write("\n\nSignal-to-noise ratio: "+SNRvalue) 
            boolstr = str(self.EnableBgButton.isChecked())               
            file.write("\n\nBackground function enabled: "+boolstr) 
            if self.EnableBgButton.isChecked() == True:
                file.write("\n\nBackground dimension: "+str(self.bg_dim)) 
                file.write("\n\nBackground decay: "+str(self.bg_decay[0])+'*1e-4 1/ns')
            if self.userdef == False:    
                if self.integrator_static == 3:
                    intstr = 'Fresnel integrals'
                elif self.userdef == False:  
                    intstr = 'Numerical trapezoidal integration'           
                elif self.integrator_static == 0:  
                    intstr = 'Adaptive numerical trapezoidal integration'        
                elif self.integrator_static == 2:  
                    intstr = 'Fresnel integrals with high discretization rate'  
            else:        
                intstr = 'Kernel matrix with Fresnel integral evaluation' 
            file.write("\n\nIntegration method: "+intstr)                                 
        file.close()     
        figsize1 = self.figure.get_size_inches()
        figsize2 = self.figure2.get_size_inches()        
        try:  
            if eval(self.configs_str["autosave"]) == True:
                k =str(self.configs_str["figure_format"])
                s = k.split(",")
                for i in range(0,len(s)):
                    for tick in self.ax.xaxis.get_major_ticks():
                        tick.label.set_fontsize(self.configs["axeslabelfontsize"]) 
                    for tick in self.ax.yaxis.get_major_ticks():
                        tick.label.set_fontsize(self.configs["axeslabelfontsize"])
                    for tick in self.ax2.xaxis.get_major_ticks():
                        tick.label.set_fontsize(self.configs["axeslabelfontsize"]) 
                    for tick in self.ax2.yaxis.get_major_ticks():
                        tick.label.set_fontsize(self.configs["axeslabelfontsize"]) 
                    self.ax.xaxis.get_label().set_fontsize(self.configs["fontsize"])  
                    self.ax2.xaxis.get_label().set_fontsize(self.configs["fontsize"])           
                    self.ax.yaxis.get_label().set_fontsize(self.configs["fontsize"])  
                    self.ax2.yaxis.get_label().set_fontsize(self.configs["fontsize"])                             
                    self.figure.set_size_inches(self.configs["xsize"], self.configs["ysize"], forward=True)
                    self.figure2.set_size_inches(self.configs["xsize"], self.configs["ysize"], forward=True)
                    self.figure.tight_layout()
                    self.figure2.tight_layout()
                    s[i] = str(s[i]).rstrip()
                    s[i] = s[i].replace(" ", "")
                    self.figure.savefig(name+strTT+"."+str(s[i]), bbox_inches='tight', papertype = 'a4', format = s[i])
                    self.figure2.savefig(name+strDD+"."+str(s[i]), bbox_inches='tight', papertype = 'a4', format = s[i])
                self.figure.set_size_inches(figsize1, forward=True)
                self.figure2.set_size_inches(figsize2, forward=True)   
                self.plot_TT()
                self.plot_DD()
        except:    
            self.figure.set_size_inches(figsize1, forward=True)
            self.figure2.set_size_inches(figsize2, forward=True)             
            self.plot_TT()
            self.plot_DD()
            self.War5 = QMessageBox.warning(self,"Error",
            "Something went wrong! Figures could not be saved.\nMaybe wrong configuration settings.",QMessageBox.Ok)              

        




    #Plot PELDOR/DEER time trace       
    def plot_TT(self):
        self.ax.clear()    
        self.ax = self.figure.add_subplot(111)
        self.ax.set_autoscaley_on(True)
        self.ax.axis('on')
        self.ax.set_xlabel(self.configs_str["xlabel_time_trace"],size=self.configs["fontsize"])
        self.ax.set_ylabel(self.configs_str["ylabel_time_trace"],size=self.configs["fontsize"])
        if self.TT_userdef == True and eval(self.configs_str["showuserTT"]) == True:
            if self.EnableBgButton.isChecked() == True:
                self.TT_usr_tmp = self.TT_usr/max(abs(self.TT_usr))
            else:    
                self.TT_usr_tmp =  self.TT_usr
            self.ax.plot(self.time_usr, self.TT_usr_tmp,color = self.configs_str["ColorUser"].replace(" ", ""),linewidth=self.configs["linewidth"] )            
        if eval(self.configs_str["title_time_trace"]) == True:
            self.ax.set_title('PELDOR/DEER trace',size=self.configs["fontsize"])
        for tick in self.ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(self.configs["axeslabelfontsize"]) 
        for tick in self.ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(self.configs["axeslabelfontsize"])
        if eval(self.configs_str["yticks_time_trace"]) == False:            
            self.ax.set_yticks([])       
        if self.EnableBgButton.isChecked() == True:
            spc = self.spc_bg_n/max(abs(self.spc_bg_n))
            self.ax.plot(self.time, spc,color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"] )               
            if self.showbg == True:
                self.ax.plot(self.time_bg, self.bg_function/max(abs(self.spc_bg_n)),color = self.configs_str["colorBG"].replace(" ", ""),linewidth=self.configs["linewidth"] )
        else:    
            self.ax.plot(self.time, self.spc_bg_n,color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"] )
            if self.showbg == True:
                self.ax.plot(self.time_bg, self.bg_function,color = self.configs_str["colorBG"].replace(" ", ""),linewidth=self.configs["linewidth"] )                  
        self.ax.margins(x = self.configs["xmargin"], y= self.configs["ymargin"])   
        self.figure.tight_layout()
        self.figure.subplots_adjust(left=0.18, bottom=0.18, right=0.96, top=0.92) 
        self.canvas.draw()   
        return




    #Detached PELDOR/DEER time trace plot and distance distribution plot
    def detach_plot_TT(self):
        if len(self.time)==1:
            return       
        if not hasattr(self, 'figure4'):    
            pass
        else:
            self.ax4.clear()      
            self.ax4 = self.figure4.add_subplot(111)
            self.ax4.set_autoscaley_on(True)
            self.ax4.axis('on')
            self.ax4.set_xlabel(self.configs_str["xlabel_time_trace"],size=self.configs["fontsize"])
            self.ax4.set_ylabel(self.configs_str["ylabel_time_trace"],size=self.configs["fontsize"])
            if self.TT_userdef == True and eval(self.configs_str["showuserTT"]) == True:
                if self.EnableBgButton.isChecked() == True:
                    self.TT_usr = self.TT_usr/max(abs(self.TT_usr))
                else:    
                    self.TT_usr =  self.TT_usr
                self.ax.plot(self.time_usr, self.TT_usr,color = self.configs_str["ColorUser"].replace(" ", ""),linewidth=self.configs["linewidth"] )              
            for tick in self.ax4.xaxis.get_major_ticks():
                    tick.label.set_fontsize(self.configs["axeslabelfontsize"]) 
            for tick in self.ax4.yaxis.get_major_ticks():
                    tick.label.set_fontsize(self.configs["axeslabelfontsize"])
            if self.EnableBgButton.isChecked() == True:
                spc = self.spc_bg_n/max(abs(self.spc_bg_n))
                self.ax4.plot(self.time, spc,color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"] )               
                if self.showbg == True:
                    self.ax4.plot(self.time_bg, self.bg_function/max(abs(self.spc_bg_n)),color = self.configs_str["colorBG"].replace(" ", ""),linewidth=self.configs["linewidth"] )
            else:    
                self.ax4.plot(self.time, self.spc_bg_n,color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"] )
                if self.showbg == True:
                    self.ax4.plot(self.time_bg, self.bg_function,color = self.configs_str["colorBG"].replace(" ", ""),linewidth=self.configs["linewidth"] )  
            self.ax4.margins(x = self.configs["xmargin"], y= self.configs["ymargin"])  
            self.figure4.tight_layout()
            self.figure.subplots_adjust(left=0.2, bottom=0.18, right=0.96, top=0.92) 
            self.toolbar2 = NavigationToolbar(self.canvas4,self.canvas4)
            self.canvas4.draw()
            self.canvas4.show()       
        if not hasattr(self, 'figure5'):    
            pass
        else:        
            self.ax5.clear()  
            self.ax5 = self.figure5.add_subplot(111)    
            self.ax5.set_autoscaley_on(False)
            self.ax5.axis('on')
            self.ax5.set_ylim([-0.01, 1.06])
            self.ax5.set_xlabel(self.configs_str["xlabel_dd"],size=self.configs["fontsize"])
            self.ax5.set_ylabel(self.configs_str["ylabel_dd"],size=self.configs["fontsize"])    
            for tick in self.ax5.xaxis.get_major_ticks():
                    tick.label.set_fontsize(self.configs["axeslabelfontsize"])    
            for tick in self.ax5.yaxis.get_major_ticks():
                    tick.label.set_fontsize(self.configs["axeslabelfontsize"])                
            if self.userdef == True:
                self.ax5.plot(self.r_usr, self.Pr_usr/max(self.Pr_usr),color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"] )
            else:    
                self.ax5.plot(self.r, self.Pr/max(self.Pr),color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"] )
            self.ax5.margins(x = self.configs["xmargin"], y= self.configs["ymargin"])     
            self.figure5.tight_layout()
            self.figure5.subplots_adjust(left=0.18, bottom=0.12, right=0.92, top=0.92) 
            self.toolbar3 = NavigationToolbar(self.canvas5,self.canvas5)
            self.canvas5.draw()
            self.canvas5.show()            
        return
        
    
    
        
    #PELDOR/DEER time trace plot     
    def plot_DD(self):  
        self.ax2.clear()
        self.ax2 = self.figure2.add_subplot(111)    
        self.ax2.set_autoscaley_on(False)
        self.ax2.axis('on')
        self.ax2.set_xlabel(self.configs_str["xlabel_dd"],size=self.configs["fontsize"])
        self.ax2.set_ylabel(self.configs_str["ylabel_dd"],size=self.configs["fontsize"])
        self.ax2.set_ylim([-0.01, 1.06])
        if eval(self.configs_str["title_dd"]) == True:
            self.ax2.set_title('Distance distribution',size=self.configs["fontsize"])
        if eval(self.configs_str["yticks_dd"]) == False:            
            self.ax2.set_yticks([])     
        for tick in self.ax2.xaxis.get_major_ticks():
                tick.label.set_fontsize(self.configs["axeslabelfontsize"])       
        for tick in self.ax2.yaxis.get_major_ticks():
                tick.label.set_fontsize(self.configs["axeslabelfontsize"])                  
        if eval(self.configs_str["yticks_dd"]) == False:            
            self.ax2.set_yticks([])                     
        if self.userdef == True:
            self.ax2.plot(self.r_usr, self.Pr_usr/max(self.Pr_usr),color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"] )
        else:    
            self.ax2.plot(self.r, self.Pr/max(self.Pr),color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"])
        self.ax2.margins(x = self.configs["xmargin"], y= self.configs["ymargin"])    
        self.figure2.tight_layout()
        self.figure2.subplots_adjust(left=0.16, bottom=0.18, right=0.98, top=0.92) 
        self.canvas2.draw()   
        return
        
        
    
        
    #PELDOR/DEER time trace fourier transform plot     
    def plot_FT(self):
        self.ax3.clear()
        self.ax3 = self.figure3.add_subplot(111)   
        self.ax3.set_autoscaley_on(False)
        self.ax3.set_ylabel('$Normalised\ \ Intensity$',size=self.configs["fontsize"])
        self.ax3.set_title('Fourier transform',size=self.configs["fontsize"])
        self.ax3.axis('on')
        self.ax3.set_xlabel('$\omega\ \mathrm{/ \ MHz}$',size=self.configs["fontsize"])
        self.ax3.set_ylim([min(self.Fourier),max(self.Fourier)+0.1*(max(self.Fourier))])
        axval1 = min([self.inputvalues[0], self.inputvalues[2],self.inputvalues[4],
                      self.inputvalues[6],self.inputvalues[8]])
        axval1 = 80.0/(axval1*axval1) 
        try:
            if self.userdef == False:
                indext0 = np.argwhere(np.abs(self.Pr) > 1e-3)
                ind = min(indext0)
                dist_tmp = self.r[ind]
            else:
                indext0 = np.argwhere(np.abs(self.Pr_usr) > 1e-3)
                ind = min(indext0)
                dist_tmp = self.r_usr[ind]                
            fac = dist_tmp**2
        except:
            fac=1.0
        self.ax3.set_xlim([-35/fac ,35/fac]) 
        self.ax3.set_yticklabels( () )
        for tick in self.ax3.xaxis.get_major_ticks():
                tick.label.set_fontsize(self.configs["axeslabelfontsize"]) 
        self.ax3.set_yticks([])                    
        self.ax3.plot(self.Frequency_region, self.Fourier,color = self.configs_str["colorL"].replace(" ", ""),linewidth=self.configs["linewidth"])
        self.figure3.tight_layout()
        self.figure3.subplots_adjust(left=0.12, bottom=0.18, right=0.98, top=0.92) 
        self.canvas3.draw()                
        return



    def open_config(self):
        self.dialog2 = QDialog()
        self.dialog2.ui = ChildConfig()
        self.dialog2.ui.setupUi(self.dialog2)
        for key in sorted(self.configs, key=str.lower, reverse=False):
            self.dialog2.ui.plainTextEdit_config.appendPlainText(str(key)+" = " +str(self.configs[key]))
        self.dialog2.ui.plainTextEdit_config.appendPlainText("") 
        for key in sorted(self.configs_str, key=str.lower, reverse=False):
            self.dialog2.ui.plainTextEdit_config.appendPlainText(str(key)+" = " +str(self.configs_str[key]))                               
        self.dialog2.ui.Accept_conf_Button.clicked.connect(self.dialog2.accept)
        self.dialog2.ui.Reject_conf_Button.clicked.connect(self.dialog2.reject)
        self.dialog2.show()
        if self.dialog2.exec_():    
            self.change_config()
            
            
    def change_config(self):
        if self.dialog2.accept:
            confstr_const =copy.copy(self.configs_str)
            t = self.dialog2.ui.plainTextEdit_config.toPlainText()
            doc =t.split('\n')
            for i in range(0,len(doc)):
                l = doc[i]
                for key in self.configs:
                    if key in l:
                        s = l.split("=")
                        s = s
                        try:
                            self.configs[key] = float(s[1])
                            if key in self.configs_lim_min.keys():
                                if self.configs[key] < self.configs_lim_min[key]:
                                    self.configs[key] = self.configs_lim_min[key]
                            if key in configs_lim_max.keys():
                                if self.configs[key] > self.configs_lim_max[key]:
                                    self.configs[key] = self.configs_lim_max[key]                              
                        except:
                            self.War6 = QMessageBox.warning(self,"Error",
                                "Something went wrong! \nWrong configuration settings.",QMessageBox.Ok)                             
                            pass
                for key in self.configs_str:
                    if key in l:
                        s = l.split("=")
                        try:       
                            self.configs_str[key] = s[1].rstrip()
                            self.configs_str[key] =self.configs_str[key].lstrip()
                        except:
                            self.War6 = QMessageBox.warning(self,"Error",
                                "Something went wrong! \nWrong configuration settings.",QMessageBox.Ok) 
                            pass
            try:
                self.make_calculation()    
            except:
                self.War6 = QMessageBox.warning(self,"Error",
                        "Something went wrong! \nWrong configuration settings.",QMessageBox.Ok) 
                self.configs_str= confstr_const
                self.make_calculation()
                pass                           
        else:
            pass
        
    def close_GUI(self):
        reply = QMessageBox.question(self, 'Message',
        "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if hasattr(self, 'figure4'):  
                self.canvas4.close() 
            if hasattr(self, 'figure5'):  
                self.canvas5.close()                 
            self.close()           
        else:
            return       
            
            
#------------------------------------------------------------------------------
#EVENT-LOOP of the SimPel2018 GUI application        
#------------------------------------------------------------------------------           
if __name__ == '__main__': 
    app_ss =  QApplication(sys.argv)
    splash_screen = QSplashScreen(QPixmap(resource_path("SimPel_splashicon.png")))
    splash_screen.show()
    app_ss.processEvents()
    start =time.time()
    while time.time() - start < 2:
        time.sleep(0.001)
        app_ss.processEvents()

    #MAIN GUI APPLICATION
    app = QApplication(sys.argv)   
    main =  SimPelDesign()
    app.processEvents()         
    main.show()   
    splash_screen.finish(main)
    sys.exit(app_ss.exec_())   
    sys.exit(app.exec_())