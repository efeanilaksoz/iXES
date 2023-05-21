from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import QTime
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  
import os
import errno
import math
from serial.tools import list_ports
import asyncio
import logging
import argparse
import platform
import threading
import time
import os
import simpleaudio
import errno
import datetime
import xml.etree.ElementTree as ET
from HR import *
from PolarH10 import *

import asyncio                  #Asynchronous I/O library to write concurrent code using the async/await syntax.
from bleak import BleakScanner  #Bluetooth Low Energy platform Agnostic Klient (Bleak) Bleak is a GATT client software, capable of connecting to BLE devices acting as GATT servers.
from bleak import BleakClient   #Bleak client used for connecting the BLE device

from acquireSRMData import *
from params import *
from readSRMData_NEW import *
from AmpCalc import *
from parameters import *
from gui_functions import *

from signal import signal, SIGPIPE, SIG_DFL  
signal(SIGPIPE,SIG_DFL) 

FORCE_UUID = "7F510019-1B15-11E5-B60B-1697F925EC7B"     #From SRM XPower datasheet, notify firmware >= 14
BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"   #From SRM XPower datasheet

ch_onoff = [1, 1, 1, 1, 1, 1, 1, 1]
amp_values  = []
plsw_values = []
angle_values = []
slope_values = []
folder = ""
results_folder = ""

#*********************************************************************************************************** 
class Xpower:
    def __init__(self, *args):            
        # Identifier 
        self.Id = args[0]
        self.Address = args[1]
        # Property related to Bleak
        self.Notifying = True
        
        # File
        # if args[2] != 'none':
        #    self.SaveByte = SaveByteStream(args[2] + '/' +'binary_' + args[0])  
#*********************************************************************************************************** 
class MainWindow(QtWidgets.QMainWindow):
    #----------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.initialize()
        self.function_connections()
    #----------------------------------------------------
    def initialize(self):
        global folder
        self.statusBar().showMessage('Starting iXES...')

        ## Find the current directory and set the folder name to run form.ui
        self.statusBar().showMessage('Parsing folder name...')

        folder = sys.path[0]
        print('Folder selected: ' + folder)
        try:
            os.makedirs(folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        ## Load the UI Page
        self.statusBar().showMessage('Opening Form.ui')
        uic.loadUi(folder +'/form.ui', self)

        #self.timeEdit.setTime(QTime(0,30,0))
        self.statusBar().showMessage('Working folder = ' + folder)
        
        self.initfromXML()
        self.click_comrefresh()
        self.stimoptions()
    #----------------------------------------------------
    def function_connections(self):

        #self.pushButton_set2default.pressed(self.initfromXML)
        self.pushButton_start.clicked.connect(run_record)
        self.pushButton_stop.clicked.connect(stop_gui)
        self.pushButton_comrefresh.clicked.connect(self.click_comrefresh)
        self.pushButton_plotstim.clicked.connect(plotstimpattern)
        self.pushButton_searchpedals.clicked.connect(self.run_search_pedals)
        self.timeEdit.timeChanged.connect(self.time_changed)
        self.pushButton_connectHR.clicked.connect(self.startHR)

        self.spinBox_amp1.editingFinished.connect(self.value_changed)
        self.spinBox_plsw1.editingFinished.connect(self.value_changed)
        self.spinBox_start1.editingFinished.connect(self.value_changed)
        self.spinBox_stop1.editingFinished.connect(self.value_changed)
        self.spinBox_range1.editingFinished.connect(self.value_changed)
        self.spinBox_slope1.editingFinished.connect(self.value_changed)
        self.horizontalSlider_range1.sliderReleased.connect(self.value_changed)
        self.checkBox_ch1.stateChanged.connect(self.value_changed)

        self.spinBox_amp3.editingFinished.connect(self.value_changed)
        self.spinBox_plsw3.editingFinished.connect(self.value_changed)
        self.spinBox_start3.editingFinished.connect(self.value_changed)
        self.spinBox_stop3.editingFinished.connect(self.value_changed)
        self.spinBox_range3.editingFinished.connect(self.value_changed)
        self.spinBox_slope3.editingFinished.connect(self.value_changed)
        self.horizontalSlider_range3.sliderReleased.connect(self.value_changed)
        self.checkBox_ch3.stateChanged.connect(self.value_changed)

        self.spinBox_amp5.editingFinished.connect(self.value_changed)
        self.spinBox_plsw5.editingFinished.connect(self.value_changed)
        self.spinBox_start5.editingFinished.connect(self.value_changed)
        self.spinBox_stop5.editingFinished.connect(self.value_changed)
        self.spinBox_range5.editingFinished.connect(self.value_changed)
        self.spinBox_slope5.editingFinished.connect(self.value_changed)
        self.horizontalSlider_range5.sliderReleased.connect(self.value_changed)
        self.checkBox_ch5.stateChanged.connect(self.value_changed)

        self.spinBox_amp7.editingFinished.connect(self.value_changed)
        self.spinBox_plsw7.editingFinished.connect(self.value_changed)
        self.spinBox_start7.editingFinished.connect(self.value_changed)
        self.spinBox_stop7.editingFinished.connect(self.value_changed)
        self.spinBox_range7.editingFinished.connect(self.value_changed)
        self.spinBox_slope7.editingFinished.connect(self.value_changed)
        self.horizontalSlider_range7.sliderReleased.connect(self.value_changed)
        self.checkBox_ch7.stateChanged.connect(self.value_changed)

        self.checkBox_veladapt.toggled.connect(self.stimoptions)
        self.checkBox_biofeedback.toggled.connect(self.stimoptions)
        self.checkBox_RPMgain.toggled.connect(self.stimoptions)

        self.spinBox_rpmgain.editingFinished.connect(self.stimoptions)
        self.spinBox_speedlimit.editingFinished.connect(self.stimoptions)

        self.timeEdit.setTime(QTime(1,0,0))
        self.checkBox_startMetronome.toggled.connect(self.Start_Metronome)

    #----------------------------------------------------
    def startHR(self):
        self.pushButton_connectHR.setText("Connecting...")
        self.pushButton_connectHR.setEnabled(False)
        rec_HR = threading.Thread(target=self.HR_record_thread)
        rec_HR.start()

    #----------------------------------------------------
    def HR_record_thread(self):
        HR_label = self.label_HR

        time = self.timeEdit.time()
        duration = time.hour()*3600 + time.minute()*60 + time.second()
        duration = duration + 60
        msg_text = "HR will be recorded for " + str(duration) + " seconds..."
        self.statusBar().showMessage(msg_text)

        record_len = duration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(record_HR(record_len, HR_label))
        self.pushButton_connectHR.setText("Connect")
        self.pushButton_connectHR.setEnabled(True)
        
    def Metronome_thread(self):
        strong_beat = simpleaudio.WaveObject.from_wave_file(folder + "/strong_beat.wav")
        
        while self.checkBox_startMetronome.isChecked() and self.label_HR.text().isnumeric():
            bpm = int(self.label_HR.text())
            interval = 60/bpm
            strong_beat.play()
            #print(self.label_HR.Value())
            threading.Event().wait(interval)

    def Start_Metronome(self):

        if self.checkBox_startMetronome.isChecked():
            start_metronome = threading.Thread(target=self.Metronome_thread)
            start_metronome.start()

    #----------------------------------------------------
    def value_changed(self):
        global amp_values, plsw_values, angle_values, slope_values, ch_onoff

        sender = self.sender()
        msg_text = "Changed something? Parameters were not effected..."

        # AMP? 
        if 'amp' in str(sender.objectName()):
            num = filter(str.isdigit, str(sender.objectName()))
            num = "".join(num)
            amp_values[int(num)-1] = int(sender.value())
            amp_values[int(num)]   = int(sender.value())
            msg_text = str(sender.objectName()) + " --> value changed --> " + "Amp =" + str(amp_values)
            self.update_XML('amp',amp_values)

        # PLSW? 
        if 'plsw' in str(sender.objectName()):
            num = filter(str.isdigit, str(sender.objectName()))
            num = "".join(num)
            plsw_values[int(num)-1] = int(sender.value())
            plsw_values[int(num)]   = int(sender.value())
            msg_text = str(sender.objectName()) + " --> value changed --> " + "Plsw =" + str(plsw_values)
            self.update_XML('plsw',plsw_values)

        # Angle? 
        if 'start' in str(sender.objectName()):
            num = filter(str.isdigit, str(sender.objectName()))
            num = "".join(num)
            range = self.calculate_range(angle_values[int(num)*2-2],angle_values[int(num)*2-1])
            angle_values[int(num)*2-2] = int(sender.value())
            angle_values[int(num)*2-1] = angle_values[int(num)*2-2] + range
            angle_values[int(num)*2-1] = angle_values[int(num)*2-1]%360
            msg_text = str(sender.objectName()) + " --> value changed --> " + "Angle =" + str(angle_values)
            print('Start Value Changed... ')
            self.update_XML('angle',angle_values)

        if 'stop' in str(sender.objectName()):
            num = filter(str.isdigit, str(sender.objectName()))
            num = "".join(num)
            angle_values[int(num)*2-1] = int(sender.value())
            msg_text = str(sender.objectName()) + " --> value changed --> " + "Angle =" + str(angle_values)
            print('Stop Value Changed... ')
            self.update_XML('angle',angle_values)

        if 'range' in str(sender.objectName()):
            num = filter(str.isdigit, str(sender.objectName()))
            num = "".join(num)
            angle_values[int(num)*2-1] = angle_values[int(num)*2-2]+int(sender.value())
            angle_values[int(num)*2-1] = angle_values[int(num)*2-1] % 360
            msg_text = str(sender.objectName()) + " --> value changed --> " + "Angle =" + str(angle_values)
            print('Range Value Changed... ')
            self.update_XML('angle',angle_values)

        if 'slope' in str(sender.objectName()):
            num = filter(str.isdigit, str(sender.objectName()))
            num = "".join(num)
            slope_values[int(num)-1] = int(sender.value())
            slope_values[int(num)]   = int(sender.value())
            msg_text = str(sender.objectName()) + " --> value changed --> " + "Slope =" + str(slope_values)
            print('Slope Value Changed... ')
            self.update_XML('slope',slope_values)

        if 'checkbox' and 'ch' in str(sender.objectName()):
            num = filter(str.isdigit, str(sender.objectName()))
            num = "".join(num)
            print("Checkbox_ch" + str(num) + " state changed to: " + str(sender.isChecked()))
            
            if not sender.isChecked():
                ch_onoff[int(num)-1] = 0
                ch_onoff[int(num)]   = 0

            if sender.isChecked():
                ch_onoff[int(num)-1] = 1
                ch_onoff[int(num)]   = 1

            msg_text = str(sender.objectName()) + " --> value changed --> " + "Channels =" + str(ch_onoff)

        self.initfromXML()
        #TODO: plot only allowed
        plotstimpattern()
        self.statusBar().showMessage(msg_text)
    #----------------------------------------------------
    def update_XML(self,param,newvalue):
        global folder

        xml_dir = folder + '/xml/' + 'default.xml'
        self.statusBar().showMessage(xml_dir)
        tree = ET.parse(xml_dir)
        root = tree.getroot()

        for child in root[0]:
            if child.tag == param:
                child.text = str(newvalue)
                #print(root.tag + '.' + child.tag[0:5] + "\t= " + child.text)
                tree.write(xml_dir)
        
        print('XML file updated...')
    #----------------------------------------------------
    def initfromXML(self):
        global folder, amp_values, plsw_values, angle_values, slope_values

        #sender = self.sender()
        #print(str(sender.objectName()))

        xmlname = 'default.xml'
        xml_dir = folder + '/xml/' + xmlname
        self.statusBar().showMessage(xml_dir)
        tree = ET.parse(xml_dir)
        root = tree.getroot()

        for child in root[0]:
            if child.tag == 'name':
                self.lineEdit_name.setText(child.text)
        
            if child.tag == 'surname':
                self.lineEdit_surname.setText(child.text)

            if child.tag == 'birthday':
                self.lineEdit_birthday.setText(child.text)

            if child.tag == 'amp':
                xml_amp = child.text.strip('][').split(', ')
                self.spinBox_amp1.setValue(int(xml_amp[0]))
                self.spinBox_amp3.setValue(int(xml_amp[2]))
                self.spinBox_amp5.setValue(int(xml_amp[4]))
                self.spinBox_amp7.setValue(int(xml_amp[6]))
        
            if child.tag == 'plsw':
                xml_plsw = child.text.strip('][').split(', ')
                self.spinBox_plsw1.setValue(int(xml_plsw[0]))
                self.spinBox_plsw3.setValue(int(xml_plsw[2]))
                self.spinBox_plsw5.setValue(int(xml_plsw[4]))
                self.spinBox_plsw7.setValue(int(xml_plsw[6]))

            if child.tag == 'angle':
                xml_angle = child.text.strip('][').split(', ')
                self.spinBox_start1.setValue(int(xml_angle[0]))
                self.spinBox_stop1.setValue(int(xml_angle[1]))
                self.spinBox_range1.setValue(self.calculate_range(xml_angle[0],xml_angle[1]))
                self.horizontalSlider_range1.setValue(self.calculate_range(xml_angle[0],xml_angle[1]))
                
                self.spinBox_start3.setValue(int(xml_angle[4]))
                self.spinBox_stop3.setValue(int(xml_angle[5]))
                self.spinBox_range3.setValue(self.calculate_range(xml_angle[4],xml_angle[5]))
                self.horizontalSlider_range3.setValue(self.calculate_range(xml_angle[4],xml_angle[5]))

                self.spinBox_start5.setValue(int(xml_angle[8]))
                self.spinBox_stop5.setValue(int(xml_angle[9]))
                self.spinBox_range5.setValue(self.calculate_range(xml_angle[8],xml_angle[9]))
                self.horizontalSlider_range5.setValue(self.calculate_range(xml_angle[8],xml_angle[9]))

                self.spinBox_start7.setValue(int(xml_angle[12]))
                self.spinBox_stop7.setValue(int(xml_angle[13]))
                self.spinBox_range7.setValue(self.calculate_range(xml_angle[12],xml_angle[13]))
                self.horizontalSlider_range7.setValue(self.calculate_range(xml_angle[12],xml_angle[13]))

            if child.tag == 'slope':
                xml_slope = child.text.strip('][').split(', ')
                self.spinBox_slope1.setValue(int(xml_slope[0]))
                self.spinBox_slope3.setValue(int(xml_slope[2]))
                self.spinBox_slope5.setValue(int(xml_slope[4]))
                self.spinBox_slope7.setValue(int(xml_slope[6]))
        
        amp_values   = [int(xml_amp[0]), int(xml_amp[1]), int(xml_amp[2]), int(xml_amp[3]), int(xml_amp[4]), int(xml_amp[5]), int(xml_amp[6]), int(xml_amp[7])] 
        plsw_values  = [int(xml_plsw[0]), int(xml_plsw[1]), int(xml_plsw[2]), int(xml_plsw[3]), int(xml_plsw[4]), int(xml_plsw[5]), int(xml_plsw[6]), int(xml_plsw[7])]
        angle_values = [int(xml_angle[0]), int(xml_angle[1]), int(xml_angle[2]), int(xml_angle[3]), int(xml_angle[4]), int(xml_angle[5]), int(xml_angle[6]), int(xml_angle[7]),int(xml_angle[8]), int(xml_angle[9]), int(xml_angle[10]), int(xml_angle[11]), int(xml_angle[12]), int(xml_angle[13]), int(xml_angle[14]), int(xml_angle[15])]
        slope_values = [int(xml_slope[0]), int(xml_slope[1]), int(xml_slope[2]), int(xml_slope[3]), int(xml_slope[4]), int(xml_slope[5]), int(xml_slope[6]), int(xml_slope[7])]
        update_stimParams(amp_values,plsw_values,angle_values,slope_values)
    #----------------------------------------------------
    def calculate_range(self,start,stop):

        range = int(stop)-int(start)
        if range < 0:
            range = range + 360

        return range
    #----------------------------------------------------
    def click_comrefresh(self):
        self.comboBox_comtest.clear()                       # Clear the combox items

        port = list(list_ports.comports())                  # list the aviable ports
        for p in port:                                  
            if p.device.__contains__('serial'):             # if name contains serial
                self.comboBox_comtest.addItem(p.device)     # add item on top 

        for p in port:                                      # then add the others
            if not p.device.__contains__('serial'):
                self.comboBox_comtest.addItem(p.device)

        if self.comboBox_comtest.findText('/dev/cu.usbserial-HMSIWVLN') == -1:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning...")
            dlg.setText("Stimuator is not connected...")
            button = dlg.exec()
            self.pushButton_start.setEnabled(False)
        
        if self.comboBox_comtest.findText('/dev/cu.usbserial-HMSIWVLN') != -1:
            self.pushButton_start.setEnabled(True)
    #----------------------------------------------------
    def time_changed(self):
        sender = self.sender()
        time = sender.time()
        StopTime = time.hour()*3600 + time.minute()*60 + time.second()
        if StopTime == 0:
            StopTime == 60
        changetime(self, StopTime)
        msg_text = str(sender.objectName()) + " --> value changed --> " + "Time = " + str(StopTime)
        self.statusBar().showMessage(msg_text)
    #----------------------------------------------------
    async def search_pedals(self):
        # Define local variables
        OtherDeviceNum = 0  #Set local variable for other BLE devices to keep the number
        SRMDeviceNum = 0    #SRM device number 

        print(">> Scanning BLE devices using BleakScanner")  
        devices = await BleakScanner.discover(timeout=10) #This will scan for 5 seconds and produce a printed list of detected devices

        for d in devices:
            if "SRM_XP_L_1690" in d.name:                                  #Check if SRM is in the name of the discovered sensor
                SRMDeviceNum = SRMDeviceNum + 1                            #Increase the SRM device number to keep track
                la = Xpower(d.name, d.address)
                print("\n",SRMDeviceNum,"SRM X-Power Sensor found:")
                print("====================================") 
                print("Name:\t\t", la.Id) 
                print("BLE Address:\t", la.Address, "(for MAC)")

                async with BleakClient(la.Address, timeout=10.0) as client:  #Connect to SRM sensor with BleakClient, 10 secs for timeout
                    try:
                        battery = await client.read_gatt_char(BATTERY_UUID)    #Use batterUUID global variable to read battery
                        SRM_battery = int(str("{0}".format(' '.join('{0:08b}'.format(x) for x in battery))),2)
                        print("Battery Level:\t",SRM_battery,"%")
                        #angle = await client.start_notify(FORCE_UUID, callback)
                        #SRM_angle = int(str('{:08b}'.format(data[j+17])+'{:08b}'.format(data[j+16])),2)
                        #print("Angle:\t",SRM_angle,"degrees")
                        await client.disconnect() 
                    except Exception as e:
                        print(e)
                print("====================================\n")
                self.label_la_address.setText(str(la.Address)[-12:])
                self.progressBar_la.setValue(int(SRM_battery))
                self.label_la.setText('Left Arm' + ' (' + str(SRM_battery) + '%)')
                       #Just increase the other device number for result
            elif "SRM_XP_R_193" in d.name:                                  #Check if SRM is in the name of the discovered sensor
                SRMDeviceNum = SRMDeviceNum + 1                            #Increase the SRM device number to keep track
                ra = Xpower(d.name, d.address)
                print("\n",SRMDeviceNum,"SRM X-Power Sensor found:")
                print("====================================") 
                print("Name:\t\t", ra.Id) 
                print("BLE Address:\t", ra.Address, "(for MAC)")

                async with BleakClient(ra.Address, timeout=10.0) as client:  #Connect to SRM sensor with BleakClient, 10 secs for timeout
                    try:
                        battery = await client.read_gatt_char(BATTERY_UUID)    #Use batterUUID global variable to read battery
                        SRM_battery = int(str("{0}".format(' '.join('{0:08b}'.format(x) for x in battery))),2)
                        print("Battery Level:\t",SRM_battery,"%")
                        #angle = await client.start_notify(FORCE_UUID, callback)
                        #SRM_angle = int(str('{:08b}'.format(data[j+17])+'{:08b}'.format(data[j+16])),2)
                        #print("Angle:\t",SRM_angle,"degrees")
                        await client.disconnect() 
                    except Exception as e:
                        print(e)
                print("====================================\n")
                self.label_ra_address.setText(str(ra.Address)[-12:])
                self.progressBar_ra.setValue(int(SRM_battery))
                self.label_ra.setText('Right Arm' + ' (' + str(SRM_battery) + '%)')
            elif "SRM_XP_L_1633" in d.name:                                  #Check if SRM is in the name of the discovered sensor
                SRMDeviceNum = SRMDeviceNum + 1                            #Increase the SRM device number to keep track
                ll = Xpower(d.name, d.address)
                print("\n",SRMDeviceNum,"SRM X-Power Sensor found:")
                print("====================================") 
                print("Name:\t\t", ll.Id) 
                print("BLE Address:\t", ll.Address, "(for MAC)")

                async with BleakClient(ll.Address, timeout=10.0) as client:  #Connect to SRM sensor with BleakClient, 10 secs for timeout
                    try:
                        battery = await client.read_gatt_char(BATTERY_UUID)    #Use batterUUID global variable to read battery
                        SRM_battery = int(str("{0}".format(' '.join('{0:08b}'.format(x) for x in battery))),2)
                        print("Battery Level:\t",SRM_battery,"%")
                        #angle = await client.start_notify(FORCE_UUID, callback)
                        #SRM_angle = int(str('{:08b}'.format(data[j+17])+'{:08b}'.format(data[j+16])),2)
                        #print("Angle:\t",SRM_angle,"degrees")
                        await client.disconnect() 
                    except Exception as e:
                        print(e)
                print("====================================\n")
                self.label_ll_address.setText(str(ll.Address)[-12:])
                self.progressBar_ll.setValue(int(SRM_battery))
                self.label_ll.setText('Left Leg' + ' (' + str(SRM_battery) + '%)')
            elif "SRM_XP_R_1556" in d.name:                                  #Check if SRM is in the name of the discovered sensor
                SRMDeviceNum = SRMDeviceNum + 1                            #Increase the SRM device number to keep track
                rl = Xpower(d.name, d.address)
                print("\n",SRMDeviceNum,"SRM X-Power Sensor found:")
                print("====================================") 
                print("Name:\t\t", rl.Id) 
                print("BLE Address:\t", rl.Address, "(for MAC)")

                async with BleakClient(rl.Address, timeout=10.0) as client:  #Connect to SRM sensor with BleakClient, 10 secs for timeout
                    try:
                        battery = await client.read_gatt_char(BATTERY_UUID)    #Use batterUUID global variable to read battery
                        SRM_battery = int(str("{0}".format(' '.join('{0:08b}'.format(x) for x in battery))),2)
                        print("Battery Level:\t",SRM_battery,"%")
                        #angle = await client.start_notify(FORCE_UUID, callback)
                        #SRM_angle = int(str('{:08b}'.format(data[j+17])+'{:08b}'.format(data[j+16])),2)
                        #print("Angle:\t",SRM_angle,"degrees")
                        await client.disconnect() 
                    except Exception as e:
                        print(e)
                print("====================================\n")
                self.label_rl_address.setText(str(rl.Address)[-12:])
                self.progressBar_rl.setValue(int(SRM_battery))
                self.label_rl.setText('Right Arm' + ' (' + str(SRM_battery) + '%)')
            else:                                                           #If SRM is not the name: Give info about the BLE scanner results
                OtherDeviceNum = OtherDeviceNum+1                           #Just increase the other device number for result

        if SRMDeviceNum == 0:
            print(">>",OtherDeviceNum ,"BLE devices were found, none of them are SRM sensors. Please check if they are ON and try again!")
            self.statusBar().showMessage('SRM sensors were NOT found, please check if they are ON and try again!')
            
        else:
            print(">>",OtherDeviceNum ,"other devices were found...")
    #----------------------------------------------------
    def run_search_pedals(self):
        self.statusBar().showMessage('Searching for SRM X-Power pedals...')
        asyncio.run(self.search_pedals())
    #----------------------------------------------------
    def stimoptions(self):
        VELOCITY_ADAPTION(self.checkBox_veladapt.isChecked())
        Biofeedback(self.checkBox_biofeedback.isChecked())
        RPM_Gain(self.checkBox_RPMgain.isChecked(),self.spinBox_rpmgain.value(),self.spinBox_speedlimit.value())
        self.statusBar().showMessage("VA = " + str(self.checkBox_veladapt.isChecked()) 
                                     + ", BF = " + str(self.checkBox_biofeedback.isChecked())
                                     + ", RG = " + str(self.checkBox_RPMgain.isChecked())
                                     )

    def test(self):
        time1 = 50*60
        time2 = 50*60-5

        self.timeEdit.setTime(QTime(0,0,0).addSecs(time1-time2))

#*********************************************************************************************************** 
def options():
    parser = argparse.ArgumentParser(description='************* IEES GO-Tryke *************')
    parser.add_argument('action', choices=['record','get_battery'],type=str, default='record', help='Choose your program: ')
    args = parser.parse_args()

    return args
#*********************************************************************************************************** 
def run_record(debug=True):
    rec = threading.Thread(target=record_thread, args=(1,))
    rec.start()
#*********************************************************************************************************** 
def record_thread(debug=True):
    # Initialize Logger
    global results_folder
    process_time = datetime.today().strftime('%Y%m%d%H%M%S')
    results_folder = sys.path[0] +'/results/'  + process_time

    resettime()
    
    try:
        os.makedirs(results_folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    log = logging.getLogger(__name__)
    if debug:
        log.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        fh = logging.FileHandler(results_folder + '/GO_Tryke_Streamer.txt')
        fh.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add the handlers to the logger
        log.addHandler(fh)
        log.addHandler(ch)
    
    # Initialize Sensors
    sensors = get_sensors(folder=results_folder)
    
    # Initialize Canceller Token
    canceller_token = CancellerToken()

    # Record Data & Store in Binfile ***********************************
    #loop = asyncio.get_event_loop()
    #ADDED
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)    
    try:
        rec_task = asyncio.gather(*(record(sensor,log,canceller_token) for sensor in sensors))
        loop.run_until_complete(rec_task)
    except:
        log.info('Fatal error: cancelling')
        disconnect_loop = asyncio.get_event_loop()
        disconnect_task = asyncio.gather(*(disconnect(sensor,log) for sensor in sensors))
        for rec in rec_task:
            rec.cancel()
        disconnect_loop.run_until_complete(disconnect_task)
    # ******************************************************************
        
    # Read bindata files
    for binfile in BINFILES:
        #print('Folder to process =' + results_folder)
        process_binfile(results_folder,binfile)
#*********************************************************************************************************** 
def run_get_battery(debug=True):

    # Initialize Logger
    log = logging.getLogger(__name__)
    if debug:
        log.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # add the handlers to the logger
        log.addHandler(ch)
    
    # Initialize Sensors
    sensors = get_sensors()
    
    #Get Battery State ***********************************
    loop_battery = asyncio.get_event_loop()
    battery_task = asyncio.gather(*(get_battery(sensor,log) for sensor in sensors))
    loop_battery.run_until_complete(battery_task)
#*********************************************************************************************************** 
def stop_gui():
    global app
    #TODO = stop the stimulation
    #CancellerToken = True
    #stim_manager.ccl_stop()
    app.quit()
    
def main():
    print('------ Starting iXES ------')
    global app
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
#*********************************************************************************************************** 
if __name__ == '__main__':
    main()
#*********************************************************************************************************** 

