from asyncio import sleep
from cProfile import label
from cmath import pi
import math
from pickle import TRUE
from statistics import mode
from turtle import color
import random
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter, time


Plsw_left = 200                 
Plsw_right = 200
Plsw_const = (Plsw_left+Plsw_right)/2
AnglePlot = 0

amp_values  = []
plsw_values = []
angle_values = []
slope_values = []

geom = 0

Biofeedback_flag = False


# CLASSES ***********************************************************************
class Muscle:
    def __init__(self, ID , phiStart, phiEnd, Amp, maxAmp,rl_start = 20 ,rl_end = 20, Plsw = 100, Plsw_ramp = False):
        self.ID = ID
        self.phiStart = phiStart            # phi0 startangle
        self.phiEnd = phiEnd                # phi1 query
        self.Amp = Amp                      # Stiumulation Amp
        self.maxAmp = maxAmp                # max Stimulation Amp at time (t)
        self.rl_start = rl_start/100        # length of ramp (start) %
        self.rl_end = rl_end/100             # length of ramp (end) %
        self.Plsw = Plsw                    # Stimulation Pulswidth [mu_s] 
        self.Gain = 1                       # used for Pulswith ramp
        self.Input_Force_Arm = 1            # used for Biofeedbeack-Closedloop
        self.Amp_limit = 120                 # limit of Amp.
        self.Plsw_ramp = Plsw_ramp          # Ramp up the Plsw
        self.applied_Plsw =  100            # default 100 [mu s]
        self.Biofeedback_ON = True          # If Biofeedback_on == True biofeedback is enabled
        self.VELOCITY_ADAPTION_ON = True    # If VELOCITY_ADAPTION_ON == True velocityadaptation is enabled

    def getAmp(self,angle):
        r = 1                       # radius (1 = unite circle) -> don't touch!

        # Check if phi surpasses 360 threshold
        if (self.phiEnd<self.phiStart):
            self.phiEnd += 360
        
        if(self.phiEnd==self.phiStart):
            print("!!Start-Stop at same Angle!!", self.ID)
            self.maxAmp=0
        

        arcMax = 2*math.pi*r*(self.phiEnd-self.phiStart)/360

        # Check if phi surpasses 360 threshold
        if (angle<self.phiStart):
            angle += 360

        l = 2*math.pi*r*(angle-self.phiStart)/360


        # t1 arcLen to stop  accel. ramp
        t1 = self.rl_start*arcMax
        # t2 arcLen to start  deccel. ramp
        t2 = arcMax - self.rl_end*arcMax

        
        # Acceleration ramp
        if (l> 0 and l<=t1):
            self.Amp = self.maxAmp/t1*l

        # Plateau
        elif (l> t1 and l<=t2):
            self.Amp = self.maxAmp

        # Decceleration ramp
        elif (l> t2 and l<=arcMax):
            self.Amp = self.maxAmp + self.maxAmp/(t2-arcMax)*(l-t2)
        else:
            self.Amp = 0

        self.Amp= int(self.Amp)

        if(self.Amp<0):                     #safety
            #print("-----|||||Amp < 0, Setting it up to 0 |||||-----")
            self.Amp=0
        if(self.Amp>self.Amp_limit):         
            self.Amp=self.Amp_limit

        self.Gain = self.Amp/self.maxAmp
    
    def update(self,maxAmp):
        self.maxAmp = maxAmp                # max stimulation Amplitute (at time (t))

    def calc_Plsw (self, const_Plsw = Plsw_const, Arm_Force_tripleweight = 0, Arm_Force_doubleweight = 0):
        if (self.Biofeedback_ON == True):
            #----------------------------
            contraction_offset = -50      #original was -50
            stand_gain = 8
            gain_t1 = 16
            treshold_1 = 250
            #linearizied PW vs. Ftan curve. ---> Theoratical PW vs. Ftan curve adapted to Seb. T.
            #----------------------------
            self.Input_Force_Arm = (3*Arm_Force_tripleweight + 2*Arm_Force_doubleweight)/5
            self.Plsw = self.Input_Force_Arm*stand_gain+contraction_offset

            if(self.Plsw > treshold_1):
                f_shift= (treshold_1-contraction_offset)/stand_gain
                self.Plsw = treshold_1 + (self.Input_Force_Arm-f_shift)*gain_t1
            
            if(self.Plsw > 500):           #saftey
                self.Plsw = 500
            if(self.Plsw < 20):             #below 10 [muS], the stimulator can not compile it. according manual...
                #print("-----PPPPP Plsw  = " + str(int(self.Plsw)) + "< 20, Setting it up to 20 |||||-----")
                #print("-----FFFFF Force = " + str(int(self.Input_Force_Arm)))
                self.Plsw = 20

            self.Plsw = int(self.Plsw)     #if you do not use integer, you have an failure expression.
        else:
            self.Plsw = int(const_Plsw)  

    def update_Plsw(self, angVel):
        if (self.VELOCITY_ADAPTION_ON == True):
            #target: rpm = 40 -> 4.1887902 [rad/s]
            velocitygain= 4.1887902/angVel
            if(velocitygain > 1.5):
                velocitygain = 1.5
        else:
            velocitygain= 1
         

        if(self.Plsw > 500):           #saftey
                self.Plsw = 500
        if(self.Plsw < 0):             #below 10 [muS], the stimulator can not compile it. according manual... lets set it to zero and see what happens
                #print("-----|||||Plsw < 0, Setting it up to 10|||||-----")
                self.Plsw = 10


        if(self.Plsw_ramp==True):
            self.applied_Plsw = int(self.Gain*self.Plsw)*velocitygain
            if(self.applied_Plsw>500):
                self.applied_Plsw =int(500)
        else:
            self.applied_Plsw = int(self.Plsw)+velocitygain
            if(self.applied_Plsw>500):
                self.applied_Plsw = int(500)

class Delay_adjustment:
    def __init__(self, delay_t0 = 0.175, delay = 0):
        self.delay_t0 = delay_t0
        self.delay = delay
    
    def initialization(self):
        self.delay = self.delay_t0

    def update(self, delta):
        self.delay += delta

        if(self.delay>0.3):     # delay can adjust between 150 to 300 milisek.
            self.delay = 0.3
        if(self.delay<0.15):
            self.delay = 0.15

#TEST----------------------------------------------------------------------------------
Amp = 40            # ST: 20mA = feeling; 40mA: start generating some Force; 60mA: contraction generate Force (max. if you go over 250 mu_s PW) | Healty person start with 20mA
Plsw_left = 99                   
Plsw_right = 99
RPMgainONOFF = 0
RPMgain = 10
Speedlimit = 50

def update_stimParams(amp, plsw, angle, slope):
    global Quad_L, Quad_R, Calf_L, Calf_R, Ham_L, Ham_R, Glut_L, Glut_R, Plsw_const
    global amp_values, plsw_values, angle_values, slope_values

    amp_values = amp
    plsw_values = plsw
    angle_values = angle
    slope_values = slope

    Quad_L = Muscle("QL",angle[0],angle[1],0,amp[0],slope[0],slope[0])
    Quad_R = Muscle("QR",shift(angle[0]),shift(angle[1]),0,amp[1],slope[1],slope[1])     #Quadriceps right
    Calf_L = Muscle("CL",angle[4],angle[5],0,amp[2],slope[2],slope[2])                   #Calve left
    Calf_R = Muscle("CR",shift(angle[4]),shift(angle[5]),0,amp[3],slope[3],slope[3])     #Calve right
    Ham_L = Muscle("HL",angle[8],angle[9],0,amp[4],slope[4],slope[4])                    #Hamstring left
    Ham_R = Muscle("HR",shift(angle[8]),shift(angle[9]),0,amp[5],slope[5],slope[5])      #Hamstring right
    Glut_L = Muscle("GL",angle[12],angle[13],0,amp[6],slope[6],slope[6])                 #Gluteus left
    Glut_R = Muscle("GL",shift(angle[12]),shift(angle[13]),0,amp[7],slope[7],slope[7])   #Gluteus right
    Plsw_const = plsw[0]

def shift(phi):
    phi += 180
    if(phi>359):
        phi-= 360
    return(phi)

def angle_validation(phi):
    if(phi>359):
        phi-= 360
    return(phi)

def PW_update(F_leftarm,F_rightarm):
    Quad_L.calc_Plsw(const_Plsw=Plsw_left, Arm_Force_doubleweight = F_leftarm, Arm_Force_tripleweight = F_rightarm)
    Calf_L.calc_Plsw(const_Plsw=Plsw_left, Arm_Force_doubleweight = F_leftarm, Arm_Force_tripleweight = F_rightarm)
    Ham_L.calc_Plsw(const_Plsw=Plsw_left, Arm_Force_doubleweight = F_leftarm, Arm_Force_tripleweight = F_rightarm)
    Glut_L.calc_Plsw(const_Plsw=Plsw_left, Arm_Force_doubleweight = F_leftarm, Arm_Force_tripleweight = F_rightarm)
            
    Quad_R.calc_Plsw(const_Plsw=Plsw_left, Arm_Force_tripleweight = F_leftarm, Arm_Force_doubleweight = F_rightarm)
    Calf_R.calc_Plsw(const_Plsw=Plsw_left, Arm_Force_tripleweight = F_leftarm, Arm_Force_doubleweight = F_rightarm)
    Ham_R.calc_Plsw(const_Plsw=Plsw_left, Arm_Force_tripleweight = F_leftarm, Arm_Force_doubleweight = F_rightarm)
    Glut_R.calc_Plsw(const_Plsw=Plsw_left, Arm_Force_tripleweight = F_leftarm, Arm_Force_doubleweight = F_rightarm)

def Biofeedback(onset = False):

    global Biofeedback_flag

    Biofeedback_flag = onset

    Quad_L.Biofeedback_ON = onset
    Calf_L.Biofeedback_ON = onset
    Ham_L.Biofeedback_ON = onset
    Glut_L.Biofeedback_ON = onset
            
    Quad_R.Biofeedback_ON = onset
    Calf_R.Biofeedback_ON = onset
    Ham_R.Biofeedback_ON = onset
    Glut_R.Biofeedback_ON = onset



def VELOCITY_ADAPTION(onset = False):
    Quad_L.VELOCITY_ADAPTION_ON = onset
    Calf_L.VELOCITY_ADAPTION_ON = onset
    Ham_L.VELOCITY_ADAPTION_ON = onset
    Glut_L.VELOCITY_ADAPTION_ON = onset
            
    Quad_R.VELOCITY_ADAPTION_ON = onset
    Calf_R.VELOCITY_ADAPTION_ON = onset
    Ham_R.VELOCITY_ADAPTION_ON = onset
    Glut_R.VELOCITY_ADAPTION_ON = onset

def RPM_Gain(onoff, gain, limit):
    global RPMgainONOFF, RPM_Gain, Speedlimit

    RPM_Gain = int(gain)
    Speedlimit = int(limit)
    RPMgainONOFF = onoff

    #print("RPM_Gain = ", onoff, " gain = ", gain, " limit = ", limit)

#Start-Stop-Angle Musclegroups (ref. left leg) in Degree [°]
Start_Quad = 300
Stop_Quad = Start_Quad+20

Start_calf = 20
Stop_calf = Start_calf+20

Start_Ham = 120
Stop_Ham = Start_Ham+20

Start_Glut = 270
Stop_Glut = Start_Glut+20

Start_Quad = angle_validation(Start_Quad)
Stop_Quad = angle_validation(Stop_Quad)
Start_calf = angle_validation(Start_calf)
Stop_calf = angle_validation(Stop_calf)
Start_Ham = angle_validation(Start_Ham)
Stop_Ham = angle_validation(Stop_Ham)
Start_Glut = angle_validation(Start_Glut)
Stop_Glut = angle_validation(Stop_Glut)

# initialize musclegroups
Quad_L = Muscle("QL",Start_Quad,Stop_Quad,0,Amp,0.2,0.2)                       #Quadriceps left
Quad_R = Muscle("QR",shift(Start_Quad),shift(Stop_Quad),0,Amp,0.2,0.2)         #Quadriceps right
Calf_L = Muscle("CL",Start_calf,Stop_calf,0,Amp,0.2,0.2)                   #Calve left
Calf_R = Muscle("CR",shift(Start_calf),shift(Stop_calf),0,Amp,0.2,0.2)     #Calve right
Ham_L = Muscle("HL",Start_Ham,Stop_Ham,0,Amp,0.2,0.2)                     #Hamstring left
Ham_R = Muscle("HR",shift(Start_Ham),shift(Stop_Ham),0,Amp,0.2,0.2)       #Hamstring right
Glut_L = Muscle("GL",Start_Glut,Stop_Glut,0,Amp,0.2,0.2)                  #Gluteus left
Glut_R = Muscle("GL",shift(Start_Glut),shift(Stop_Glut),0,Amp,0.2,0.2)    #Gluteus right

# initialize delay
muscledelay = Delay_adjustment()
muscledelay.initialization()


# Stimulation-------------------------------------------------------------------

last_stimulation = perf_counter()  # every Stimulation command has to be recorded, to not get an overflow in the communication (system delay)
Timer=0
Stim_comand_break= 0.002

starttime=0

def stimulation (Angle,Amp,AngVel,stim_manager, delta_delay):
    global last_stimulation, Timer, starttime, Start_Quad, AnglePlot
    global Plsw_left, Plsw_right, Plsw_const, Stim_comand_break
    global Quad_L, Quad_R, Calf_L, Calf_R, Ham_L, Ham_R ,Glut_L, Glut_R, RPMgainONOFF
    global amp_values, plsw_values, angle_values, slope_values
    global RPM_Gain, Speedlimit, Biofeedback_flag

        
    muscledelay.update(delta_delay)         #[s] => (empirical_offset_angle*pi)/(180*measuredAngularvelocity)=offsetgain [s] ( default 0.1 [s])
                  
    #Calculate virtual Angel, according to the  Angularvelocity (trigger stimulation earlier to get the mechanical contraction at the right place)
    
    
    Angvel_degree= AngVel/pi*180
    offset=Angvel_degree*muscledelay.delay
    Angle=int(Angle+offset)
    Angle=angle_validation(Angle)
    AnglePlot = Angle
    
    #if the last Stimulation was to close, skip the rest of the stimulation and try it in the next callback.
    
    Timer = perf_counter()- last_stimulation
    if(Timer>Stim_comand_break): 
        
        if(AngVel>0.3): #2.86 rpm

            if RPMgainONOFF and (AngVel*9.5492968 > Speedlimit):
                gain = int(((AngVel*9.5492968 - Speedlimit)/9.5492968)*RPM_Gain)
                amp_rpm_gain = [item + gain for item in amp_values]
                update_stimParams(amp_rpm_gain,plsw_values,angle_values,slope_values)
                #print('RPM gain is on = ' + str(int(gain)))
                #print('RPM gain is on = ' + str(amp_rpm_gain))

            Stim_comand_break=0.002 # take the first measurement point within one data package from the sensors and discard the rest (if not, you get laggs)
            
            #update the musclegroupparameter
            Quad_L.update(amp_values[0])         #Quadriceps left
            Quad_R.update(amp_values[1])         #Quadriceps right
            Calf_L.update(amp_values[2])         #Calve left
            Calf_R.update(amp_values[3])         #Calve right
            Ham_L.update(amp_values[4])          #Hamstring left
            Ham_R.update(amp_values[5])          #Hamstring right
            Glut_L.update(amp_values[6])         #Gluteus left
            Glut_R.update(amp_values[7])         #Gluteus right

            Quad_L.getAmp(Angle)
            Quad_R.getAmp(Angle)
            Calf_L.getAmp(Angle) 
            Calf_R.getAmp(Angle)
            Ham_L.getAmp(Angle)
            Ham_R.getAmp(Angle) 
            Glut_L.getAmp(Angle)
            Glut_R.getAmp(Angle)

            Quad_L.update_Plsw(angVel= AngVel)                         
            Quad_R.update_Plsw(angVel= AngVel)                       
            Calf_R.update_Plsw(angVel= AngVel)  
            Calf_L.update_Plsw(angVel= AngVel)                       
            Ham_L.update_Plsw(angVel= AngVel)                        
            Ham_R.update_Plsw(angVel= AngVel)                        
            Glut_L.update_Plsw(angVel= AngVel)                        
            Glut_R.update_Plsw(angVel= AngVel)        

            if Biofeedback_flag == False:
                stim_manager.ccl_update(mode = {1: 'single', 2: 'single', 3: 'single', 4: 'single', 5: 'single', 6: 'single', 7: 'single', 8: 'single'},
                                    pulse_width = { 1: int(Plsw_const), 2: int(Plsw_const),
                                                    3: int(Plsw_const), 4:int(Plsw_const),
                                                    5: int(Plsw_const),  6: int(Plsw_const), 
                                                    7: int(Plsw_const), 8: int(Plsw_const)},
                                    pulse_current = {1: int(Quad_L.Amp), 2: int(Quad_R.Amp),
                                                     3: int(Calf_L.Amp), 4:int(Calf_R.Amp),
                                                     5: int(Ham_L.Amp),  6: int(Ham_R.Amp), 
                                                     7: int(Glut_L.Amp), 8: int(Glut_R.Amp)})

            if Biofeedback_flag == True:
                stim_manager.ccl_update(mode = {1: 'single', 2: 'single', 3: 'single', 4: 'single', 5: 'single', 6: 'single', 7: 'single', 8: 'single'},
                                    pulse_width = { 1: int(Quad_L.applied_Plsw), 2: int(Quad_R.applied_Plsw),
                                                    3: int(Calf_L.applied_Plsw), 4:int(Calf_R.applied_Plsw),
                                                    5: int(Ham_L.applied_Plsw),  6: int(Ham_R.applied_Plsw), 
                                                    7: int(Glut_L.applied_Plsw), 8: int(Glut_R.applied_Plsw)},
                                    pulse_current = {1: int(Quad_L.Amp), 2: int(Quad_R.Amp),
                                                     3: int(Calf_L.Amp), 4:int(Calf_R.Amp),
                                                     5: int(Ham_L.Amp),  6: int(Ham_R.Amp), 
                                                     7: int(Glut_L.Amp), 8: int(Glut_R.Amp)})

            #print("Calf Left Amp: "+ str(Calf_L.Amp)+" Plsw:"+ str(Calf_L.applied_Plsw))
            #print("Ham  Left Amp: "+ str(Ham_L.Amp) +" Plsw:"+ str(Ham_L.applied_Plsw))
            #print("Glut Left Amp: "+ str(Glut_L.Amp)+" Plsw:"+ str(Glut_L.applied_Plsw))

            last_stimulation=perf_counter()

            if RPMgainONOFF and AngVel*9.5492968>Speedlimit:
                amp_values = [item - gain for item in amp_values]
        else:
            stim_manager.ccl_update(mode = {1: 'single', 2: 'single', 3: 'single', 4: 'single', 5: 'single', 6: 'single', 7: 'single', 8: 'single'},
                                    pulse_width = { 1: 0, 2: 0, 
                                                    3: 0, 4: 0, 
                                                    5: 0, 6: 0, 
                                                    7: 0, 8: 0},
                                    pulse_current = {1: 0, 2: 0,
                                                    3: 0, 4: 0,
                                                    5: 0, 6: 0, 
                                                    7: 0, 8: 0})
            #sleep(0.002)                                      
            Stim_comand_break=1 # reduce computional effort during non-cycling
            last_stimulation=perf_counter()
            print("Paused", end=" >> ", flush=True)
            #plotstimpattern()

def plotstimpattern():
    #print("Plotting Stimulation Parameters...")

    # Plot
    global AnglePlot, geom
    
    #plt.close('all')
    r = np.arange(0, 360, 1)
    Quad = np.empty([len(r)])
    calf = np.empty([len(r)])
    ham= np.empty([len(r)])
    glut = np.empty([len(r)])
    baseline = np.zeros([len(r)])
    np.seterr(invalid='ignore')
    theta = np.deg2rad(AnglePlot)*r/r

    for i in range(len(r)):
        Quad_L.getAmp(r[i])
        Quad[i] = Quad_L.Amp
        Calf_L.getAmp(r[i])
        calf[i] = Calf_L.Amp
        Ham_L.getAmp(r[i])
        ham[i] = Ham_L.Amp
        Glut_L.getAmp(r[i])
        glut[i] = Glut_L.Amp

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    mngr = plt.get_current_fig_manager()
    #mngr.window.setGeometry(0, 0, 640, 524)

    plt.ion()
    ax.plot(np.deg2rad(r),Quad,color='r', label = "Quadriceps")
    ax.fill_between(np.deg2rad(r),Quad, facecolor='r', alpha=0.25)
    ax.plot(np.deg2rad(r),calf,color = 'g', label = "Calf")
    ax.fill_between(np.deg2rad(r),calf, facecolor='g', alpha=0.25)
    ax.plot(np.deg2rad(r),ham, color = 'b', label = "Hamstrings")
    ax.fill_between(np.deg2rad(r),ham, facecolor='b', alpha=0.25)
    ax.plot(np.deg2rad(r),glut, color = 'y', label = "Gluteus")
    ax.fill_between(np.deg2rad(r),glut, facecolor='y', alpha=0.25)
    ax.plot(np.deg2rad(r),baseline,color='k', label = "Baseline = 0 [mA]")
    ax.plot(theta,r)

    ax.legend(loc="lower left",fancybox=True, framealpha=1, shadow=True, borderpad=1,bbox_to_anchor=(-0.37, -0.1))
    ax.set_theta_direction(-1)
    ax.set_theta_offset(pi/2)
    ax.set_rmax(100)
    ax.set_rmin(-100)
    ax.set_thetagrids([0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330])
    ax.set_rticks([20,40,60,80])    # Less radial ticks
    ax.set_rlabel_position(-22.5)   # Move radial labels away from plotted line
    ax.grid(True)
    ax.set_title("Stimulationpattern", va='bottom')
    fig.canvas.manager.set_window_title('Stimulation Pattern Window')

    if (plt.fignum_exists(fig.number) and fig.number > 1):
        #print("Figure " + str(fig.number) + " already exists, updating previous one...")
        plt.close(fig.number-1)
    
    plt.show()

