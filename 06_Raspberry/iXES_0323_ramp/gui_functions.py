from PyQt6 import QtWidgets, uic, QtGui
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  
import os
import errno
import math


from parameters import *

def connect_all(self):
        # Buttons
        self.pushButton_start.clicked.connect(click_start)
        self.pushButton_pause.clicked.connect(click_pause)
        self.pushButton_stop.clicked.connect(click_stop)
        
def click_start():
        print("Start button was clicked...")

def click_pause():
        print("Pause button was clicked...")

def click_stop():
        print("Stop button was clicked...")



"""
def setTime(self):
        # Set date time
        self.lineEdit_time.setText(time_show)
        self.lineEdit_date.setText(date_show)

def setParams(self):
        # Set date time
        self.lineEdit_time.setText(time_show)
        self.lineEdit_date.setText(date_show)

        # Set Stimulation parameters
        #CH1
        self.lineEdit_amp1.setText(str(Amp[0]))
        self.lineEdit_plsw1.setText(str(Plsw[0]))
        self.lineEdit_start1.setText(str(Start_Angle[0]))
        self.lineEdit_stop1.setText(str(Stop_Angle[0]))
        self.lineEdit_range1.setText(str(Range_Angle[0]))
        self.horizontalSlider_start1.setValue(Start_Angle[0])
        #CH2        
        self.lineEdit_amp2.setText(str(Amp[1]))
        self.lineEdit_plsw2.setText(str(Plsw[1]))
        self.lineEdit_start2.setText(str(Start_Angle[1]))
        self.lineEdit_stop2.setText(str(Stop_Angle[1]))
        self.lineEdit_range2.setText(str(Range_Angle[1]))
        self.horizontalSlider_start2.setValue(Start_Angle[1])
        #CH3
        self.lineEdit_amp3.setText(str(Amp[2]))
        self.lineEdit_plsw3.setText(str(Plsw[2]))
        self.lineEdit_start3.setText(str(Start_Angle[2]))
        self.lineEdit_stop3.setText(str(Stop_Angle[2]))
        self.lineEdit_range3.setText(str(Range_Angle[2]))
        self.horizontalSlider_start3.setValue(Start_Angle[2])
        #CH4
        self.lineEdit_amp4.setText(str(Amp[3]))
        self.lineEdit_plsw4.setText(str(Plsw[3]))
        self.lineEdit_start4.setText(str(Start_Angle[3]))
        self.lineEdit_stop4.setText(str(Stop_Angle[3]))
        self.lineEdit_range4.setText(str(Range_Angle[3]))
        self.horizontalSlider_start4.setValue(Start_Angle[3])
        #CH5
        self.lineEdit_amp5.setText(str(Amp[4]))
        self.lineEdit_plsw5.setText(str(Plsw[4]))
        self.lineEdit_start5.setText(str(Start_Angle[4]))
        self.lineEdit_stop5.setText(str(Stop_Angle[4]))
        self.lineEdit_range5.setText(str(Range_Angle[4]))
        self.horizontalSlider_start5.setValue(Start_Angle[4])
        #CH6
        self.lineEdit_amp6.setText(str(Amp[5]))
        self.lineEdit_plsw6.setText(str(Plsw[5]))
        self.lineEdit_start6.setText(str(Start_Angle[5]))
        self.lineEdit_stop6.setText(str(Stop_Angle[5]))
        self.lineEdit_range6.setText(str(Range_Angle[5]))
        self.horizontalSlider_start6.setValue(Start_Angle[5])
        #CH7
        self.lineEdit_amp7.setText(str(Amp[6]))
        self.lineEdit_plsw7.setText(str(Plsw[6]))
        self.lineEdit_start7.setText(str(Start_Angle[6]))
        self.lineEdit_stop7.setText(str(Stop_Angle[6]))
        self.lineEdit_range7.setText(str(Range_Angle[6]))
        self.horizontalSlider_start7.setValue(Start_Angle[6])
        #CH8
        self.lineEdit_amp8.setText(str(Amp[7]))
        self.lineEdit_plsw8.setText(str(Plsw[7]))
        self.lineEdit_start8.setText(str(Start_Angle[7]))
        self.lineEdit_stop8.setText(str(Stop_Angle[7]))
        self.lineEdit_range8.setText(str(Range_Angle[7]))
        self.horizontalSlider_start8.setValue(Start_Angle[7])
"""