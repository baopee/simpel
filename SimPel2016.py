"""
@author: Stephan Rein

GUI using Calculation_PELDOR_TT routines for simulation of
PELDOR time traces

Main GUI is SimPel2016.py
QT framework is used.

If the program does not work there might be libaries missing.
Try:

- sudo apt-get install python-qt4

- sudo apt-get install python3-numpy python3-scipy

Have fun :)

(c) Stephan Rein, University of Freiburg
"""

"""Calculation of PELDOR time traces"""


import numpy as np
#import matplotlib.pyplot as plt
from PyQt4 import QtCore, QtGui
from Calcualtion_PELDOR_TT import calculate_time_trace
from Calcualtion_PELDOR_TT import add_background
from Calcualtion_PELDOR_TT import add_noise
from Calcualtion_PELDOR_TT import calculate_time
from Calcualtion_PELDOR_TT import calculate_distance_distr
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


import sys # Need sys so that we can pass argv to QApplication

import SimPel # This file holds MainWindow of SimPel


class SimPelDesign(QtGui.QMainWindow, SimPel.Ui_SimPel2016):
    def __init__(self):
        
        super(self.__class__, self).__init__()
        self.setupUi(self)  

        QtGui.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)   
                
        """Define matplotlib as widget"""
        self.figure = Figure()
        self.figure.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)        
        self.layout = QtGui.QVBoxLayout(self.widgetplot)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.ax = self.figure.add_subplot(111)  
        
        """Define matplotlib as widget2"""
        self.figure2 = Figure()
        self.figure2.set_facecolor('white')
        self.canvas2 = FigureCanvas(self.figure2)        
        self.layout2 = QtGui.QVBoxLayout(self.Distancedistrwindow)
        self.layout2.addWidget(self.canvas2)
        self.setLayout(self.layout2)
        self.ax2 = self.figure2.add_subplot(111)  
        
        
        """Define matplotlib as widget3"""
        self.figure3 = Figure()
        self.figure3.set_facecolor('white')
        self.canvas3 = FigureCanvas(self.figure3)        
        self.layout3 = QtGui.QVBoxLayout(self.FTwindow)
        self.layout3.addWidget(self.canvas3)
        self.setLayout(self.layout3)
        self.ax3 = self.figure3.add_subplot(111)  
        
        """Toolbar for Time trace figure"""
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()  
        
        """DetachFigure + Toolbar for Time trace figure"""
        self.figure4 = Figure()
        self.canvas4 = FigureCanvas(self.figure4)  
        self.ax4 = self.figure4.add_subplot(111)
        
        """Default Vaules for PEDLOR Calculation"""
        self.inputvalues = np.zeros(11)
        #Distances
        self.inputvalues[0] = 2
        self.inputvalues[2] = 2
        self.inputvalues[4] = 2
        self.inputvalues[6] = 2
        self.inputvalues[8] = 2
        #sigma
        self.inputvalues[10] = 0.1
        #coefficients
        self.inputvalues[1] = 1        
        
        """Default Vaules other aspectes for PEDLOR Calculation"""
        #Modulation depth
        self.moddepth = np.zeros(1)
        self.moddepth[0] = 0.2
        #Background decay    
        self.bg_decay = np.zeros(1)
        self.bg_decay[0] = 1
        self.bg_dim = 3
        self.bg_on = 1
        self.showbg = 0
        self.time_bg = np.zeros(1)
        #Timescale and stepsize   
        self.timescale = 1500.0
        self.stepsize = 8.0
        self.time = np.zeros(1)
        self.time[0] = 1000
        self.SNRratio  =20
        self.noislevel = 0
        self.noise_on = 0
        self.noisefunction = 0
        
        """Set Savebutton on off"""
        self.save_on = False

        """Allocation of temporary arrays"""
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
        """Define other simulation settings"""
        # Integrator 1 trapezoidal, 0 adaptive
        self.integrator = 1
        self.superadap = False
        self.superadap
        
        
        """***********EVENTS,BUTTONS,FIELDS***********"""
        
        
        """Start Calculation"""
        self.Startbutton.clicked.connect(self.make_calculation) 

        """Zoome in, pan or detach PELDOR tt window"""
        self.zoomButtonPeldorTT.clicked.connect(self.zoominPELDORTT)   
        self.panPELDORTT.clicked.connect(self.makepanPELDORTT)
        self.DetachButton.clicked.connect(self.makeDetachfigure) 
        
        
        """Distances"""
        self.Distance1edit.textChanged.connect(self.read_dist1) 
        self.Distance2edit.textChanged.connect(self.read_dist2)
        self.Distance3edit.textChanged.connect(self.read_dist3) 
        self.Distance4edit.textChanged.connect(self.read_dist4) 
        self.Distance5edit.textChanged.connect(self.read_dist5) 
        
        """Coefficients"""
        self.Coeff1edit.textChanged.connect(self.read_coeff1) 
        self.Coeff2edit.textChanged.connect(self.read_coeff2)
        self.Coeff3edit.textChanged.connect(self.read_coeff3) 
        self.Coeff4edit.textChanged.connect(self.read_coeff4) 
        self.Coeff5edit.textChanged.connect(self.read_coeff5) 
        
        """TimeStepsize and Timescla"""
        self.Timescalebox.valueChanged.connect(self.set_stepsize)
        self.Timescalebox.lineEdit().setReadOnly(True)
        self.Timescaleedit.textChanged.connect(self.read_timescale) 
        
        """Modulation depth"""
        self.Moddepthedit.textChanged.connect(self.read_moddpeth)
        
        """Background Settings"""
        self.Bgdecayedit.textChanged.connect(self.read_bgdecy)
        self.BgDimbox.valueChanged.connect(self.set_bgdim)
        self.BgDimbox.lineEdit().setReadOnly(True)
        self.EnableBgButton.toggled.connect(lambda:self.btn1state(self.EnableBgButton))
        self.ShowBGButton.toggled.connect(lambda:self.btn2state(self.ShowBGButton))
        
        """Standard deviation"""
        self.Sigmaedit.textChanged.connect(self.read_sigma)   
        
        """Noise"""
        self.EnableNoiseButton.toggled.connect(lambda:self.btn3state(self.EnableNoiseButton))
        self.SNR_edit.textChanged.connect(self.read_SNR) 
        
        """Integration method"""
        self.ButtonTrapezoidal.toggled.connect(lambda:self.btn4state(self.ButtonTrapezoidal))        
        self.Checkbox_superadaptive.stateChanged.connect(lambda:self.use_superadaptive_Gaussian(self.Checkbox_superadaptive))
        self.ButtonFullyAdaptive.toggled.connect(lambda:self.btn5state(self.ButtonFullyAdaptive))
        self.ButtonAdaptive.toggled.connect(lambda:self.btn6state(self.ButtonAdaptive))
        
        """Save file"""
        self.Savebutton.clicked.connect(self.save_file)
        """Close GUI""" 
        self.Closebutton.clicked.connect(self.close_GUI)  

        
        
    def plot_TT(self):
        ''' PELDOR time trace '''
        self.ax.clear()    
        self.ax = self.figure.add_subplot(111)
        self.ax.set_autoscaley_on(False)
        self.ax.axis('on')
        self.ax.set_xlabel('time / ns',size=11)
        self.ax.set_ylabel('Intensity',size=11)
        self.ax.set_ylim([min(self.spc_bg_n)-
        0.1*abs(min(self.spc_bg_n)),max(self.spc_bg_n)+
        0.1*abs(max(self.spc_bg_n))])
        self.ax.set_xlim([min(self.time),max(self.time)])
        self.ax.set_title('PELDOR time trace',size=11)
        for tick in self.ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(10) 
        for tick in self.ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(10)
        self.figure.tight_layout()
        self.ax.plot(self.time, self.spc_bg_n)
        if self.showbg == True:
            self.ax.plot(self.time_bg, self.bg_function)          
        self.ax.hold(True)
        self.canvas.draw()   
        return

    def detach_plot_TT(self):
        ''' PELDOR time trace '''
        if len(self.time)==1:
            return
        self.ax4.clear()      
        self.ax4 = self.figure4.add_subplot(111)
        self.ax4.set_autoscaley_on(False)
        self.ax4.axis('on')
        self.ax4.set_xlabel('time / ns',size=11)
        self.ax4.set_ylabel('Intensity',size=11)
        self.ax4.set_ylim([min(self.spc_bg_n)-
        0.1*abs(min(self.spc_bg_n)),max(self.spc_bg_n)+
        0.1*abs(max(self.spc_bg_n))])
        self.ax4.set_xlim([min(self.time),max(self.time)])
        self.ax4.set_title('PELDOR time trace',size=11)
        for tick in self.ax4.xaxis.get_major_ticks():
                tick.label.set_fontsize(10) 
        for tick in self.ax4.yaxis.get_major_ticks():
                tick.label.set_fontsize(10)
        self.ax4.plot(self.time, self.spc_bg_n)
        if self.showbg == True:
            self.ax4.plot(self.time_bg, self.bg_function)          
        self.ax4.hold(True)
        self.canvas4.draw()
        self.canvas4.show()
        return
        
    def plot_DD(self):
        ''' PELDOR time trace '''   
        self.ax2.clear()
        self.ax2 = self.figure2.add_subplot(111)    
        self.ax2.set_autoscaley_on(False)
        self.ax2.axis('on')
        self.ax2.set_xlabel('r / nm',size=10)
        self.ax2.set_ylim([0,max(self.Pr)+0.1*(max(self.Pr))])
        self.ax2.set_xlim([1.5,8.0])
        self.ax2.set_title('Distance distribution',size=10)
        self.ax2.set_yticklabels( () )
        for tick in self.ax2.xaxis.get_major_ticks():
                tick.label.set_fontsize(8) 
        self.figure2.tight_layout()
        self.ax2.plot(self.r, self.Pr)
        self.ax2.hold(True)
        self.canvas2.draw()   
        return
        
    def plot_FT(self):
        ''' PELDOR time trace '''   
        self.ax3.clear()
        self.ax3 = self.figure3.add_subplot(111)   
        self.ax3.set_autoscaley_on(False)
        self.ax3.set_title('Fouriertransformed',size=10)
        self.ax3.axis('on')
        self.ax3.set_xlabel('w / MHz',size=10)
        #self.ax2.set_ylabel('Intensity')
        self.ax3.set_ylim([0,max(self.Fourier)+0.1*(max(self.Fourier))])
        """set the axis adaptive"""
        axval1 = min([self.inputvalues[0], self.inputvalues[2],self.inputvalues[4],
                      self.inputvalues[6],self.inputvalues[8]])
        axval1 = 80.0/(axval1*axval1) 
        self.ax3.set_xlim([-axval1 ,axval1]) 
        self.ax3.set_yticklabels( () )
        for tick in self.ax3.xaxis.get_major_ticks():
                tick.label.set_fontsize(8) 
        self.figure3.tight_layout()
        self.ax3.plot(self.Frequency_region, self.Fourier)
        self.ax3.hold(True)
        self.canvas3.draw()                
        return
        
    def make_calculation(self):      
        """Enable Save"""
        self.save_on = True       
        
        """Distance Distribution Calculation"""        
        self.Pr,self.r = calculate_distance_distr(self.inputvalues)
        
        """Main PELDOR Calculation"""
        self.JarasprogressBar.setValue(0)
        self.time = calculate_time(self.timescale,self.stepsize)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)  

        self.spectrum,self.Fourier,self.Frequency_region = calculate_time_trace(self.inputvalues,
                                        self.time,self.moddepth,self.integrator,
                                        self.superadap,self.JarasprogressBar) 
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor) 
        self.JarasprogressBar.setValue(0)
        
        self.make_noise()  
                
        self.make_background()                         
                                                        
        """Make plot of TT (Time trace), DD(Distance distribution)"""                          
        self.plot_TT()
        self.plot_DD()
        self.plot_FT()
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor) 
        return

        
    def make_background(self):
        
        if self.bg_on == 1:
            self.spc_bg_n,self.bg_function= add_background(self.spc_n,self.time,self.bg_dim,
                                  self.bg_decay,self.moddepth)
        else:
            self.spc_bg_n = self.spc_n               
            self.bg_function = np.zeros(len(self.spc_n))
        
        """Get the elements for positive times"""
        n = 0
        while n < len(self.time):
            if self.time[n] >= 0:
                break
            n = n+1
               
        self.time_bg = self.time[n::]
        self.bg_function = self.bg_function[n::]

        """Make plot of TT (Time trace), DD(Distance distribution)"""                          
        self.plot_TT()    
        return

    def make_noise(self):
        if self.noise_on == 1:
            self.noislevel =(max(self.spc_bg_n))/self.SNRratio 
            self.spc_n,self.noisefunction= add_noise(self.spectrum,self.noislevel)
        else:
            self.spc_n = self.spectrum
        self.make_background()        
        return
        
    """Funny add ons"""        
    def zoominPELDORTT(self):        
        self.toolbar.zoom()
    def makepanPELDORTT(self):        
        self.toolbar.pan()
    def makeDetachfigure(self):        
        self.detach_plot_TT()
        
    """Distances"""     
    def read_dist1(self, text): 
        if float(text) <= 8.0 and float(text) >= 1:
            self.inputvalues[0] = float(text)
        else:
            self.Distance1edit.setText(str(self.inputvalues[0]))

    def read_dist2(self, text2): 
        if float(text2) <= 8.0 and float(text2) >= 1:
            self.inputvalues[2] = float(text2)
        else:
            self.Distance2edit.setText(str(self.inputvalues[2]))
            
    def read_dist3(self, text3): 
        if float(text3) <= 8.0 and float(text3) >= 1:
            self.inputvalues[4] = float(text3)
        else:
            self.Distance3edit.setText(str(self.inputvalues[4]))

    def read_dist4(self, text4): 
        if float(text4) <= 8.0 and float(text4) >= 1:
            self.inputvalues[6] = float(text4)
        else:
            self.Distance4edit.setText(str(self.inputvalues[6]))
            
    def read_dist5(self, text5): 
        if float(text5) <= 8.0 and float(text5) >= 1:
            self.inputvalues[8] = float(text5)
        else:
            self.Distance5edit.setText(str(self.inputvalues[8]))
            
            
    """Coefficients"""     
    def read_coeff1(self, text): 
        if float(text) <= 1.0 and float(text) >= 0:
            self.inputvalues[1] = float(text)
        else:
            self.Coeff1edit.setText(str(self.inputvalues[1]))

    def read_coeff2(self, text2): 
        if float(text2) <= 1.0 and float(text2) >= 0:
            self.inputvalues[3] = float(text2)
        else:
            self.Coeff2edit.setText(str(self.inputvalues[3]))
            
    def read_coeff3(self, text3): 
        if float(text3) <= 1.0 and float(text3) >= 0:
            self.inputvalues[5] = float(text3)
        else:
            self.Coeff3edit.setText(str(self.inputvalues[5]))

    def read_coeff4(self, text4): 
        if float(text4) <= 1.0 and float(text4) >= 0:
            self.inputvalues[7] = float(text4)
        else:
            self.Coeff4edit.setText(str(self.inputvalues[7]))
            
    def read_coeff5(self, text5): 
        if float(text5) <= 1.0 and float(text5) >= 0:
            self.inputvalues[9] = float(text5)
        else:
            self.Coeff5edit.setText(str(self.inputvalues[9])) 
            
    """PELDOR stepsize and time scale"""
    def set_stepsize(self, value): 
        self.stepsize = value          

    def read_timescale(self, ts): 
        if float(ts) < 10000.0 and float(ts) >= 0:
            self.timescale = float(ts)
        else:
            self.Timescaleedit.setText(str(self.timescale)) 
            
    """PELDOR stepsize"""
    def read_moddpeth(self, md): 
        if float(md) <= 1.0 and float(md) >= 0:
            self.moddepth[0] = float(md)
        else:
            self.Moddepthedit.setText(str(self.moddepth[0])) 
        if self.moddepth[0]==0:
            self.moddepth[0] = 0.00001        
        return

    """PELDOR stepsize"""
    def read_bgdecy(self, dc): 
        if float(dc) <= 100000.0 and float(dc) >= 0:
            self.bg_decay[0] = float(dc)
        else:
            self.Bgdecayedit.setText(str(self.bg_decay[0]))      
        
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
        self.plot_TT()   
        return    

        
    def btn3state(self,noiseenaleb):
        if noiseenaleb.isChecked() == True:
            self.noise_on = 1
        else:
            self.noise_on = 0
        self.make_noise()
        return 

    def read_sigma(self,sigval):
        if float(sigval) <= 0.5 and float(sigval) >= 0:
            self.inputvalues[10] = float(sigval)
        else:
            self.Sigmaedit.setText(str(self.inputvalues[10])) 
        if self.inputvalues[10]<0.1:
            self.moddepth[0] = 0.1        
        return


    """Set signal-to-noise ratio"""
    def read_SNR(self, dc): 
        if float(dc) <= 100000.0 and float(dc) >= 0:
            self.SNRratio = float(dc)
        else:
            self.SNR_edit.setText(str(self.SNRratio))      
        
        self.make_noise()   
        return
        
    """Set up integration method"""
    def btn4state(self,integr):
        if integr.isChecked() == True:
            self.integrator = 1
        else:
            self.integrator = 0
            
        return 

    def btn5state(self,integr):
        if integr.isChecked() == True:
            self.integrator = 2
            if self.superadap == True:
                self.superadap = False
                self.Checkbox_superadaptive.setCheckState(False)
        else:
            self.integrator = 1            
        return 
        
    def btn6state(self,integr):
        if integr.isChecked() == True:
            self.integrator = 0
        else:
            self.integrator = 1            
        return         

    def use_superadaptive_Gaussian(self,adaptiveon):     
        if (adaptiveon.isChecked() == True and not self.integrator == 2):
            self.superadap = True
        elif(adaptiveon.isChecked() == True and self.integrator == 2): 
            self.superadap = False
            self.Checkbox_superadaptive.setCheckState(False)
        else:
            self.superadap = False

    """SAVE OUTPUT""" 
    def save_file(self):
        #if self.save_on == False:
         #   return
        saveFile = QtGui.QAction("&Save File", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save File')
        self.file_save()
        
    def file_save(self):
    
        dialog = QtGui.QFileDialog()
        dialog.setFilter("Text files (*.txt)")
        #dialog.setNameFilters("Text files (*.txt)")
        #dialog.selectNameFilter("Text files (*.txt)")        
        name= dialog.getSaveFileName(self, 'Save File',' ', 
                "*.txt (*.txt);;*dat (*.dat)")
                
        if not name:
            return False
            
        name = str(name)     
        #lname = name.lower()   
        if not (name.endswith('.txt') or name.endswith('.dat')) :
            name += '.txt' #default .txt ending         
         
        filetyp = '.txt'
        if '.txt' in name:
            pos = name.index('.txt')
            filetyp = '.txt'
            name = name[0:pos]
        elif '.dat' in name:
            pos = name.index('.dat')
            filetyp = '.dat'
            name = name[0:pos]
            
        """SAVE ALL SIMULATED DATA"""
        strTT = '_Time_Trace'
        strFT = '_Fourier_Transformed'
        strDD = '_Distance_Distribution'
        strBG = '_Backgound_Function'
        
        file = open(name+strTT+filetyp,'w')     
        tmparra = np.array( (self.time,self.spc_bg_n))        
        np.savetxt(file, (np.transpose(tmparra)),fmt = '%.18g',delimiter='   ')
        file.close()        
        
        file = open(name+strFT+filetyp,'w')     
        tmparra = np.array( (self.Frequency_region, self.Fourier))        
        np.savetxt(file, (np.transpose(tmparra)),fmt = '%.18g',delimiter='   ')
        file.close()  
        
        file = open(name+strDD+filetyp,'w')     
        tmparra = np.array( (self.r,self.Pr))        
        np.savetxt(file, (np.transpose(tmparra)),fmt = '%.18g',delimiter='   ')
        file.close() 
        
        file = open(name+strBG+filetyp,'w')     
        tmparra = np.array( (self.time_bg, self.bg_function))        
        np.savetxt(file, (np.transpose(tmparra)),fmt = '%.18g',delimiter='   ')
        file.close()           
        
    def close_GUI(self):
        print("event")
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.close()
        else:
            return 


        
if __name__ == '__main__': # if we're running file directly and not importing it


    """Main GUI EVENT LOOP"""  
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    main =  SimPelDesign()   
    app.processEvents()         
    main.show()   # Show SimPel 
    app.exec_()   # close application
 
    
