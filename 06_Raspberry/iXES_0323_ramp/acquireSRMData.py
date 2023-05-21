import asyncio
from cmath import pi
#from timeit import _Timer
import keyboard
import platform
import asyncio
from cmath import cos, pi
import platform
from matplotlib.pyplot import fill
import numpy as np

import signal
import sys

import stimulator

from time import time
from time import perf_counter

from bleak import BleakClient

from params import *
from readSRMData import *
from AmpCalc import *

from AngleCalc import *
from PID import *

from PyQt6.QtCore import QTime


## Global Variables

StopTime = int(0)       #seconds      
Start_Ramp = int (10)   #seconds
REF_TIME = 0

AngVel = 0
timeflag = 1
LineEdit_duration = 0
LineEdit_time = 0

Label_Force_ll = 0 
Label_Force_rl = 0 

Label_Force_la = 0 
Label_Force_ra = 0 

Label_cadence  = 0
Label_trikespeed = 0

Bar_force_ll = 0
Bar_force_rl = 0
Bar_force_la = 0
Bar_force_ra = 0

gui = 0

# CLASSES ***********************************************************************
class Xpower:
    def __init__(self, *args):            
        # Identifier 
        self.Id = args[0]
        self.Address = args[1]
        # Property related to Bleak
        self.Notifying = False
        
        # File
        if args[2] != 'none':
            self.SaveByte = SaveByteStream(args[2] + '/' +'binary_' + args[0])
            #self.SaveByte = SaveByteStream(args[2] +'binary_' + args[0])
                      
class SaveByteStream:
    def __init__(self, filename):
        self.filename = filename
        self.saving = False
    def start(self):
        if not self.saving:
            self.file = open(self.filename, 'wb')
            self.saving = True
    def write_in_file(self, data):
        if self.saving:
            self.file.write(bytearray(data))
    def stop(self):
        if self.saving:
            self.saving = False
            self.file.close()

class CancellerToken:
    def __init__(self):
        self.Cancelled = False
        self.IsSendingEvents = False
    async def check_ui_cancel(self,log):
        while not self.Cancelled:
            # End Recording
            #if keyboard.is_pressed('e') and self.Cancelled == False:
            #    self.Cancelled = True
            #    break
            await asyncio.sleep(2) # ms loop every 2000ms

# FUNCTIONS*************************************************************************
def changetime(self, newtime):
    global StopTime, LineEdit_duration, LineEdit_time
    global Label_Force_ll, Label_Force_rl
    global Label_Force_la, Label_Force_ra
    global Label_cadence, Label_trikespeed
    global Bar_force_ll, Bar_force_rl
    global Bar_force_la, Bar_force_ra
    global gui

    gui = self

    StopTime = int(newtime)
    Date = datetime.today().strftime('%d/%m/%Y')
    #self.lineEdit_date.setText(Date + ' : ' +str(StopTime))
    LineEdit_duration = self.lineEdit_date
    LineEdit_time = self.timeEdit_elapsed

    Label_Force_ll = self.label_force_ll
    Label_Force_rl = self.label_force_rl

    Label_Force_la = self.label_force_la
    Label_Force_ra = self.label_force_ra

    Label_cadence  = self.label_cadence
    Label_trikespeed = self.label_trikespeed

def resettime():
    global REF_TIME
    REF_TIME = time.time()

def get_sensors(folder='none',fake=False):
    # SRM X power pedals  addresses
    """
    AADF9E9C-31CC-2E21-16D4-6ACBB2951E11: SRM_XP_L_1690 - LA - Windows: CE26BE9A5CE5
    8AC69371-26D9-2FC5-9E7F-C2F6369161C5: SRM_XP_L_1633 - LL - Windows: DFFCB858E9BF
    0C2F83F5-6F09-6872-01DB-157A3F8344DE: SRM_XP_R_1556 - RL - Windows: D1BC2A90A931
    80498D0E-9F8D-8533-A2C2-CD82194E173E: SRM_XP_R_193 - RA 
    """
    if fake:
        # FAKE SENSOR
        adress = '05647B2D-C327-48D4-8763-FB3A35C8A293'
        phone = Xpower("phone", adress)
        sensors = [phone]
    else:    
        ll_addr = ("DF:FC:B8:58:E9:BF" # for Windows/Linux System
                    if platform.system() != "Darwin"
                    else '8AC69371-26D9-2FC5-9E7F-C2F6369161C5' # for MAC OS System
                    )
        rl_addr = ("D1:BC:2A:90:A9:31" # for Windows/Linux System
                    if platform.system() != "Darwin"
                    else '0C2F83F5-6F09-6872-01DB-157A3F8344DE' # for MAC OS System
                    )
        la_addr = ("CE:26:BE:9A:5C:E5" # for Windows/Linux System
                    if platform.system() != "Darwin"
                    else 'AADF9E9C-31CC-2E21-16D4-6ACBB2951E11' # for MAC OS System
                    )
        ra_addr = ("D6:37:1E:3E:73:3C" # for Windows/Linux System
                    if platform.system() != "Darwin"
                    else '80498D0E-9F8D-8533-A2C2-CD82194E173E' # for MAC OS System
                    )
                    
        ll = Xpower("ll", ll_addr,folder)
        rl = Xpower("rl", rl_addr,folder)
        la = Xpower("la", la_addr,folder)
        ra = Xpower("ra", ra_addr,folder)
        #sensors = [ll, rl, la, ra]

    return ll, la, ra ,rl

# ASYNC FUNCTIONS******************************************************************
async def disconnect(sensor,log):       
    async with BleakClient(sensor.Address,timeout=20.0) as client:
        if client.is_connected:
            #await client.stop_notify(FORCE_UUID)
            await client.disconnect()
        if not client.is_connected:
            log.info(f"{sensor.Id} properly disconnected.")
async def get_battery(sensor,log):
    log.info(f"starting {sensor.Address} battery loop")
    async with BleakClient(sensor.Address, timeout=10.0) as client:

        try:
            battery = await client.read_gatt_char(BATTERY_UUID)
            sensor.Battery = int(str("{0}".format(' '.join('{0:08b}'.format(x) for x in battery))),2)
            log.info(f"Battery State of {sensor.Id}: {sensor.Battery}%")
            await client.disconnect()
        except Exception as e:
            print(e)    

async def record(sensor,log,canceller_token):

    global stim_manager                                                             # Stimulator
    global Quad_L, Quad_R, Calf_L, Calf_R, Ham_L, Ham_R ,Glut_L, Glut_R             # Muscles
    global Force_LA, Force_RA, Force_LL, Force_RL                                   # Force_states
    global StopTime, Start_Ramp
    global Start_Quad, Stop_Quad
    global Ang_PID, muscledelay, AngVel, Fatigue_PID
    global LineEdit_duration

    #Set important Startparameter:
    #Biofeedback(False)
    #VELOCITY_ADAPTION(False)
                                   
    disconnected_event = asyncio.Event()
    notifying_event = asyncio.Event()

    # for RehaStim
    config_dict = {
        'port': '/dev/cu.usbserial-HMSIWVLN', #'/dev/ttyUSB0' /dev/tty.usbserial-HMSIWVLN'
        'channel_stim': [1, 2, 3, 4, 5, 6, 7, 8], # [QR, QL] ....
        'channel_lf': [],
        'n_factor': 1,
        'ts1': 29,              # Stimulation freq in wavelength [20ms = 50Hz, 30ms = 33Hz, 40 ms = 25Hz]
        'ts2': 1.5
    }
    stim_manager = stimulator.Stimulator(config_dict)
    stim_manager.ccl_initialize()

    # initialize Sensor Force Groups

    Force_LA = Force_state("LA")
    Force_RA = Force_state("RA")
    Force_LL = Force_state("LL")
    Force_RL = Force_state("RL")

    Force_LA.init_rollgaussian()
    Force_RA.init_rollgaussian()
    Force_LL.init_rollgaussian()
    Force_RL.init_rollgaussian()

    Force_LA.init_rollgaussian_fatigue()
    Force_RA.init_rollgaussian_fatigue()
    Force_LL.init_rollgaussian_fatigue()
    Force_RL.init_rollgaussian_fatigue()

    # initialize PID-Controllers


    Ang_PID = PID(P=-0.05,I=-0.01,D=-0.005) 
    #Ang_PID = PID(P=0,I=0,D=0)  
    Ang_PID.setWindup(1)
    Ang_PID.sample_time = 1

    Fatigue_PID = PID(P= 0.4 ,I=0.08,D= 1)
    # be aware: the more trained a person is, the higher the ratio is, so the error will be.
    # this leads to a faster regulation!!!
    # -> eventually work with an level set: if avg ratio is below a certain lv enhance the pearameter, else you regulate almost nothing
    # Fatigue_PID = PID(P=0,I=0,D=0)
    Fatigue_PID.setWindup(1)
    Fatigue_PID.sample_time = 0.5
    Fatigue_PID.Amplitude = Amp
    Fatigue_PID.setstartAMP(Amp,Quad_L.Amp_limit)
    

    S_tar = stimulation_target(Start_Quad,Stop_Quad,0.4,0.25)
    targ_Ang= targetAngle(Amp,Plsw_left,S_tar)
    Ang_PID.SetPoint=targ_Ang


    # NOTIF CALLBACK *******************
    def callback(sender, data): 

        # Define global variable that will be updated in this function
        global AngVel, Plsw_left, Plsw_right, Plsw_const ,Amp
        global Start_Quad, Stop_Quad, StopTime
        global Quad_L, Quad_R, Calf_L, Calf_R, Ham_L, Ham_R, Glut_L, Glut_R
        global Ang_PID, muscledelay, AngVel, Fatigue_PID
        global Force_LA, Force_RA, Force_LL, Force_RL, Ftan_la, Ftan_ra
        global Angle_ll, Angle_rl, timeflag
        global Label_Force_ll, Label_Force_rl
        global Label_Force_la, Label_Force_ra
        global Label_cadence, Label_trikespeed
        global Bar_force_ll, Bar_force_rl
        global Bar_force_la, Bar_force_ra
        global gui

        if not sensor.Notifying: 
            log.info(f"Sensor {sensor.Id} begins notify at {int((time.time()-REF_TIME)*1000)} ms")
            sensor.Notifying = True
            notifying_event.set()

        else:
            # Write in File
            timestamp = int((time.time()-REF_TIME)*1000)

            # if timestamp%100 == 0:
            #     # print(str(time))
            #     strong_beat = simpleaudio.WaveObject.from_wave_file('/Users/rehalab/Desktop/iXES_Anil/Tests/290922_QuadTest/strong_beat.wav')
            #     strong_beat.play()

            #Smoothstart to reduce spasticity
            if (timestamp < (Start_Ramp+5)*1000):
                start_gain= timestamp/(Start_Ramp*1000)
                start_gain = min(start_gain,1)
                Amp = int(abs(Fatigue_PID.StartAmp*start_gain))

            if (Amp > Quad_L.Amp_limit):
                Amp = Quad_L.Amp_limit

            Amp = int(abs(Amp))
            PLSW_l = int(abs(Quad_L.Plsw))
            PLSW_r= int(abs(Quad_R.Plsw))

            sensor.SaveByte.write_in_file(timestamp.to_bytes(4, byteorder='little', signed=False))
            sensor.SaveByte.write_in_file(data)
            sensor.SaveByte.write_in_file(Amp.to_bytes(4, byteorder='little', signed=False))
            sensor.SaveByte.write_in_file(PLSW_l.to_bytes(4, byteorder='little', signed=False))
            sensor.SaveByte.write_in_file(PLSW_r.to_bytes(4, byteorder='little', signed=False))
            
            # Check for Arm sensors (for force data)
            if (sensor.Id == "la"):
                try:
                    Ftan_la = int(twos_comp(int(str('{:08b}'.format(data[9])+'{:08b}'.format(data[8])),2),16)/10)
                except:
                    Ftan_la = int(abs(Force_LA.rollgaussian))

                try:
                    Angle_la = int(str('{:08b}'.format(data[13])+'{:08b}'.format(data[12])),2)
                except:
                    Angle_la = int(Force_LA.Angle)

                Ftan_la = -1 * Ftan_la
                Force_LA.add_measuringpoint(Ftan_la,Angle_la)

                if(Force_LA.updatePID == True):
                    Force_LA.move_rollgaussian
                    Force_RA.move_rollgaussian
                    PW_update(int(abs(Force_LA.rollgaussian)),int(abs(Force_RA.rollgaussian)))
                    Force_LA.updatePID = False

                    if gui.checkBox_displayFarms.isChecked():
                        gui.label_force_la.setText(str(int(round(Ftan_la))))

            if (sensor.Id == "ra"):

                try:
                    Ftan_ra = int(twos_comp(int(str('{:08b}'.format(data[9])+'{:08b}'.format(data[8])),2),16)/10)
                except:
                    Ftan_ra = int(abs(Force_RA.rollgaussian))
                
                try:
                    Angle_ra = int(str('{:08b}'.format(data[13])+'{:08b}'.format(data[12])),2)
                except:
                    Angle_ra = int(Force_RA.Angle)
                
                Ftan_ra = -1 * Ftan_ra
                Force_RA.add_measuringpoint(Ftan_ra,Angle_ra)

                if(Force_RA.updatePID == True):
                    Force_LA.move_rollgaussian
                    Force_RA.move_rollgaussian
                    PW_update(abs(Force_LA.rollgaussian),abs(Force_RA.rollgaussian))
                    Force_RA.updatePID = False

                    if gui.checkBox_displayFarms.isChecked():
                        gui.label_force_ra.setText(str(int(round(Ftan_ra))))

            # Check for leg sensors (for angle data)
            if (sensor.Id == "ll"):

                try:
                    Ftan_ll = int(twos_comp(int(str('{:08b}'.format(data[9])+'{:08b}'.format(data[8])),2),16)/10)
                except:
                    Ftan_ll = int(0)

                try:
                    Angle_ll = int(str('{:08b}'.format(data[13])+'{:08b}'.format(data[12])),2)
                except:
                    Angle_ll = int(Force_LL.Angle)

                try:
                    AngVel_ll = abs(twos_comp(int(str('{:08b}'.format(data[15])+'{:08b}'.format(data[14])),2),16)/1024)
                except:
                    AngVel_ll = AngVel


                Force_LL.add_measuringpoint(Ftan_ll,Angle_ll)

                if(Force_LL.updatePID==True):
                    Fatigue_PID.Amptoken = True
                    Fatigue_PID.updateFatigue()
                    S_tar = stimulation_target(Start_Quad,Stop_Quad,0.4,0.25)                                                 #calculate new target of stimulation
                    targ_Ang= targetAngle(Amp,Plsw_left,S_tar, muscle_fatigue=Fatigue_PID.Musclefatigue)                      #calculate new target Angle of mean force
                    Ang_PID.SetPoint=targ_Ang                                                                                 #new set point for the PID
                    Ang_PID.update(np.rad2deg(cmath.phase(Force_LL.rollgaussian)))                                            #calculate Error in [ms]
                    #update delay time

                    stimulation(Angle=Angle_ll,Amp=Amp,AngVel=AngVel_ll, stim_manager=stim_manager, delta_delay=Ang_PID.output/1000)
                    
                    # QUADRICEPS
                    print("---------------------------NEW Cycle------------------------------------")
                    print("Quad Left Amp: "+ str(Quad_L.Amp)+" ||||  Plsw:"+ str(int(Plsw_const)))
                    print("Quad Right Amp: "+ str(Quad_L.Amp)+" ||||  Plsw:"+ str(int(Plsw_const)))
                    print("Electromecanical delay [ms]:" + str((muscledelay.delay*1000)))
                    print("targets Angle: "+str(targ_Ang)+" <--->  Angle of applied Force: "+str(np.rad2deg(cmath.phase(Force_LL.rollgaussian))))
                    print("real (fatigue adjusted) Amp: " + str(Fatigue_PID.Amplitude))
                    print("Biofeedback: " + str(Quad_L.Biofeedback_ON) + "   ||||  Velocity adaption: " + str(Quad_L.VELOCITY_ADAPTION_ON))
                    print("Timestmp: "+str(int(timestamp/1000))+" sek  |||| Progress: "+str(round(timestamp/(StopTime*1000),2)*100)+"%")
                    #print("Angle Left Leg:" + str(int(Angle_ll)) + "Angle Right Leg:" + str(int(Angle_rl)))
                    print("---------------------------END Cycle------------------------------------")
                    
                    LineEdit_duration.setText(str(int(round(timestamp/(StopTime*1000),2)*100))+"%")
                    LineEdit_time.setTime(QTime(0,0,0).addSecs(int(timestamp/1000)))

                    if gui.checkBox_displayFlegs.isChecked():
                        gui.label_force_ll.setText(str(int(round(Ftan_ll))))

                    if gui.checkBox_displayCadence.isChecked():
                        gui.label_cadence.setText(str(int(round(AngVel_ll*9.5493))))

                    if gui.checkBox_TrikeSpeed.isChecked():
                        gui.label_trikespeed.setText("NaN")

                else:
                    stimulation(Angle=Angle_ll,Amp=Amp,AngVel=AngVel_ll, stim_manager=stim_manager, delta_delay=0)
                    #no update of the delaytime
                    Fatigue_PID.Amptoken = False
            
            if (sensor.Id == "rl"):
                try:
                    Ftan_rl = int(twos_comp(int(str('{:08b}'.format(data[9])+'{:08b}'.format(data[8])),2),16)/10)
                except:
                    Ftan_rl = int(0)
                # Get force angle and velocity values
                try:
                    Angle_rl = int(str('{:08b}'.format(data[13])+'{:08b}'.format(data[12])),2)
                except:
                    Angle_rl = int(Force_RL.Angle)

                Force_RL.add_measuringpoint(Ftan_rl,Angle_rl)

                if(Force_RL.updatePID == True):
                    Force_RL.move_rollgaussian
                    Force_LL.move_rollgaussian
                    PW_update(abs(Force_LL.rollgaussian),abs(Force_RL.rollgaussian))
                    Force_RL.updatePID = False

                    if gui.checkBox_displayFlegs.isChecked():
                        gui.label_force_rl.setText(str(int(round(Ftan_rl))))


            if(timestamp > 300000*1000):
                if(Fatigue_PID.FATIGUE_CONTROL_ON == False):
                    Force_LA.force_before_n_cycle.fill(Force_LA.rollgaussian_fatigue)
                    Force_RA.force_before_n_cycle.fill(Force_RA.rollgaussian_fatigue)
                    Force_LL.force_before_n_cycle.fill(Force_LL.rollgaussian_fatigue)
                    Force_RL.force_before_n_cycle.fill(Force_RL.rollgaussian_fatigue)
                    print("Fatigue enabeld")
                Fatigue_PID.FATIGUE_CONTROL_ON = False
            else:
                Fatigue_PID.FATIGUE_CONTROL_ON = False
                
            #enabling the Fatigue Closed-loop after x ms
            if(Fatigue_PID.FATIGUE_CONTROL_ON == True and AngVel > 2.5):
                if(Fatigue_PID.Amptoken==True):
                    #setpoint is an array by the length of the gaussian_fatigue [n] filter: t-n cycles filterd values are safed
                    setpoint_left = Force_LL.force_before_n_cycle/Force_RA.force_before_n_cycle
                    setpoint_right =Force_RL.force_before_n_cycle/Force_LA.force_before_n_cycle
                    setpoint = (setpoint_left+setpoint_right)/2
                    backstep = int(len(setpoint)/4)

                    Fatigue_PID.SetPoint = abs(setpoint[backstep])
                    Fatigue_PID.update(abs(setpoint[0]))


                    Fatigue_PID.Amplitude += Fatigue_PID.output
                    Amp = int(round(Fatigue_PID.Amplitude))
                    Fatigue_PID.Amptoken==False

                    #print("---------------------------Fatigue_Regulation------------------------------------")
                    #print("setpoint: " + str(float(abs(setpoint[backstep])))+ "  feedbackvalue: " + str(float(abs(setpoint[0]))))
                    #print("-------------------------END_Fatigue_Regulation----------------------------------")

                    if(Amp < 35):
                        Amp = 35
            else:
                Fatigue_PID.FATIGUE_CONTROL_ON = False
                        
            Fatigue_PID.Amptoken = False


            if (timestamp > StopTime*1000 and timestamp < StopTime*1010):
                print('Time is up, cancelling: ' + str(timestamp), end="\r")
                canceller_token.Cancelled = True
                #client.disconnect()
                disconnected_event.set()
                #client.set_disconnected_callback(None)
                stim_manager.ccl_stop()
                sleep(0.01)
               

    # UNSOLICITED DISCONNECT CALLBACK***
    def disconnected_callback(client):
        if not canceller_token.Cancelled and sensor.Notifying:
            log.warning(f"Sensor {sensor.Id} got disconnected!") 
            disconnected_event.set()
            client.set_disconnected_callback(None)
    #***********************************
    
    # Open Binary File
    sensor.SaveByte.start()
    log.info(f"Starting sensor {sensor.Address} recording")

    # Start Rec Loop
    while not canceller_token.Cancelled:
        
        try:
            # Connection          
            async with BleakClient(
                sensor.Address, disconnected_callback = disconnected_callback,timeout=5.0,use_cached = False
            ) as client:
                
                if client.is_connected:
                    log.info(f"Sensor {sensor.Id} is connected")
                    # ********************************************
                    # Record
                    try:
                        # Wait for notification (if none, enter except)
                        await client.start_notify(FORCE_UUID, callback)
                        await asyncio.sleep(0)
                        await asyncio.wait_for(notifying_event.wait(),1)

                        # Wait for a potential unsolliciated disconnection or keypress event
                        await asyncio.wait({canceller_token.check_ui_cancel(log), disconnected_event.wait()}, return_when=asyncio.FIRST_COMPLETED)

                        if canceller_token.Cancelled:
                            await client.stop_notify(FORCE_UUID)
                            await asyncio.sleep(0)
                            await client.disconnect()
                            await asyncio.sleep(0)
                            if not client.is_connected:
                                log.info(f"End of recording: Sensor {sensor.Id} got disconnected properly")
                                await asyncio.sleep(0)
                        else:
                            disconnected_event.clear()

                    except:
                        await client.stop_notify(FORCE_UUID)
                        await asyncio.sleep(0)
                        await client.disconnect()
                        if not sensor.Notifying:
                            log.warning(f"Cannot notify sensor {sensor.Id}. Retrying...")
                    # ********************************************
        except: # log warning
            log.error(f"Cannot (re)connect to sensor {sensor.Id}. Retrying...")

    # Close Binary File
    sensor.SaveByte.stop()
    print("Stopping stim_manager...")
    stim_manager.ccl_stop()
    print("Stopping metronome...")
