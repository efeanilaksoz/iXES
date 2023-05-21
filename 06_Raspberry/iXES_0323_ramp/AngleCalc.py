
from cProfile import label
from itertools import count
from multiprocessing.connection import wait
from random import randint
from time import perf_counter, sleep
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import cm
import cmath
from cmath import pi
from math import sqrt, exp

from AmpCalc import Muscle



#define Classes-------------------------------------------------------------------------

class Force_state:
    def __init__(self,ID,inital_count = 0, inital_measuringpoint = complex(0+0j), initial_Forcemean= 0+0j, initial_Angle = 0, crank_length = 0.125) -> None:
        self.ID             = ID
        self.count          = inital_count                
        self.Forcesum       = inital_measuringpoint
        self.Forcemean      = initial_Forcemean
        self.Angle          = initial_Angle
        self.timestamp      = perf_counter()
        self.crank_length   = crank_length
        self.updatePID      = False

    
    def reset(self):
        self.count = 0               
        self.Forcesum = complex(0 + 0j)

    def calc_mean(self):
        r,theta = cmath.polar(self.Forcesum)                                               #convert complex numbre to r = Force and theta = mean Angle
        #sleep(1) #uncomment during testing
        #delta_time = perf_counter()-self.timestamp
        self.timestamp=perf_counter()
        self.Forcemean = cmath.rect((r/(self.count)), theta)  #cmath.rect(r, phi) Output in N
        self.updatePID = True
        self.move_rollgaussian()
        self.move_rollgaussian_fatigue()
        
 
    def add_measuringpoint(self,Force,Angle2):
        # inread the force directly from the bin stream
        # inread the angle (in degree) directly from the bin stream
        self.updatePID = False
        Force = max(Force, 0)

        if(Angle2>359):
            Angle2 -= 360

        self.count += 1               
        

        if(self.ID == "LA"):
            self.Forcesum += cmath.rect(Force,np.deg2rad(90)) #cmath.rect(r, phi)
        elif(self.ID == "RA"):
            self.Forcesum += cmath.rect(Force,np.deg2rad(90)) #cmath.rect(r, phi)
        else:
            self.Forcesum += cmath.rect(Force,np.deg2rad(Angle2)) #cmath.rect(r, phi)

        if((self.Angle-Angle2)>300):
            self.calc_mean()
            #sleep(0.001)
            self.reset()
            

        self.Angle = Angle2

    def init_rollgaussian(self, length=12, sigma=2):
        "rule of thumb: to capture full size of the filter: min_length = 3*sigma*dimension of the filter"
        self.g_factor=gauss(length, sigma)+1j*gauss(length, sigma)
        self.angle_storage_cos = np.ones(len(self.g_factor))
        self.angle_storage_sin = np.ones(len(self.g_factor))

    def move_rollgaussian(self):
        self.angle_storage_cos=np.roll(self.angle_storage_cos,1)
        self.angle_storage_cos[0]= np.real(self.Forcemean)
        self.rollgaussian_cos = sum(np.real(self.g_factor)*self.angle_storage_cos)*sqrt(2)
        self.angle_storage_sin=np.roll(self.angle_storage_sin,1)
        self.angle_storage_sin[0]= np.imag(self.Forcemean)
        self.rollgaussian_sin = sum(np.imag(self.g_factor)*self.angle_storage_sin)*sqrt (2)
        
        self.rollgaussian=(self.rollgaussian_cos+1j*self.rollgaussian_sin)

    def init_rollgaussian_fatigue(self, length=100, sigma=33):
        "rule of thumb: to capture full size of the filter length = 3*sigma*dimension of the filter"
        self.g_factor_fatigue=gauss(length, sigma)+1j*gauss(length, sigma)
        self.angle_storage_cos_fatigue = np.ones(len(self.g_factor_fatigue))
        self.angle_storage_sin_fatigue = np.ones(len(self.g_factor_fatigue))
        self.force_before_n_cycle = np.ones(len(self.g_factor_fatigue), dtype=complex)

    def move_rollgaussian_fatigue(self):
        self.angle_storage_cos_fatigue=np.roll(self.angle_storage_cos_fatigue,1)
        self.angle_storage_cos_fatigue[0]= np.real(self.Forcemean)
        self.rollgaussian_cos_fatigue = sum(np.real(self.g_factor_fatigue)*self.angle_storage_cos_fatigue)*sqrt(2)
        self.angle_storage_sin_fatigue=np.roll(self.angle_storage_sin_fatigue,1)
        self.angle_storage_sin_fatigue[0]= np.imag(self.Forcemean)
        self.rollgaussian_sin_fatigue = sum(np.imag(self.g_factor_fatigue)*self.angle_storage_sin_fatigue)*sqrt (2)
        
        self.rollgaussian_fatigue=(self.rollgaussian_cos_fatigue+1j*self.rollgaussian_sin_fatigue)
        self.force_before_n_cycle=np.roll(self.force_before_n_cycle,1)
        self.force_before_n_cycle[0]=(self.rollgaussian_fatigue)

            
#define functions-----------------------------------------------------------------------

def gauss(n=5,sigma=1):
    r = range(-int(n-1),1)
    filter =  [1 / (sigma * sqrt(2*pi)) * exp(-float(x)**2/(2*sigma**2)) for x in r]
    y=np.array(filter, dtype=np.float32)
    y = y/(sum(y)*sqrt(2))
    
    return np.flip(y)


def stimulation_target(phi_Startquad,phi_Endquad,T1,T2):
    if(phi_Startquad>phi_Endquad):
        phi_Endquad += 360
    
    #calculating target force according to Stimulationintensity
    #Cent_Stim =(-T2+1)/(2-T2-T1)
    Arclength = phi_Endquad-phi_Startquad
    target_stimulation= int(phi_Startquad+Arclength*(1-T2))

    if(target_stimulation>359):
        target_stimulation -= 360
    
    #print(target_stimulation)
    
    return target_stimulation



def targetAngle(Amp,PW,target_stimulation,muscle_fatigue = 1):

    maximalPW=250       # define maximal values (Start of plateau-phase)
    maximalAmp=80       # define maximal values (Start of plateau-phase) 
    target_nostim = 68  # ST = 65
    dw_factor = float(0.7) * (muscle_fatigue**(-1))     # the stronger the participant is, the  lower this factor can be set

    

    # Calculating Stimulationintensity

    if(Amp<maximalAmp):
        Ampintensity= Amp/maximalAmp
    else:
        Ampintensity= 1+(Amp-maximalAmp)/(3*maximalAmp)
    
    if(PW<maximalPW):
        PWintensity= PW/maximalPW
    else:
        PWintensity= 1+(PW-maximalPW)/(6*maximalPW)

    StimuInt = float(Ampintensity*PWintensity)
    

    #calculation weighted mean target angle

   

    target_Angle_sin = (math.sin(np.deg2rad(target_nostim))*dw_factor + math.sin(np.deg2rad(target_stimulation))*StimuInt)/(dw_factor+StimuInt)
    target_Angle_cos = (math.cos(np.deg2rad(target_nostim))*dw_factor + math.cos(np.deg2rad(target_stimulation))*StimuInt)/(dw_factor+StimuInt)
  
    target_Angle = np.rad2deg(np.arctan2(target_Angle_sin, target_Angle_cos))

    return (target_Angle)


#Test---------------------------------------------------------------------------------------------------------------------
Testmode = 0

if(Testmode == 1):
    def angle_validation(phi):
        if(phi>359):
            phi-= 360
        return(phi)

    M_ftg = 1
    Start_Quad = 305
    Stop_Quad = Start_Quad+120

    Start_Quad = angle_validation(Start_Quad)
    Stop_Quad = angle_validation(Stop_Quad)

    S_tar = stimulation_target(Start_Quad,Stop_Quad,0.4,0.25)

    test_amp = np.arange(0, 125, 1)
    test_PW = np.arange(0, 500, 1)

    matrix = [[0 for i in range(len(test_amp))] for j in range(len(test_PW))]

    #print(np.size(matrix))

    X,Y = np.meshgrid(test_amp,test_PW)

    for i in range(len(test_PW)):
        for j in range(len(test_amp)):
            matrix[i][j]= targetAngle(i,j,S_tar,M_ftg)




    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.contour3D(X, Y, matrix, cmap=cm.coolwarm, levels=100)
    ax.set_ylabel('PW')
    ax.set_zlabel('Target Angle')



    plt.show()

if(Testmode == 2):
    test_f = Force_state("TL")
    test_f.init_rollgaussian()
    test_f.init_rollgaussian_fatigue()

    r = np.arange(0, 361, 1)
    Testleg = np.empty([len(r)])

    for i in range(len(r)):
        if(i<90):
            Force= randint(0,75)
        elif(i<180):
            Force= randint(-30,30)
        elif(i<270):
            Force= randint(-100,10)
        else:
            Force= randint(-50,20)

        
        Testleg[i] = Force

        test_f.add_measuringpoint(Force,i)

    print("Force (Pos_avg) [N]=" , abs(test_f.Forcemean), "Angle [Deg] = ", np.rad2deg(cmath.phase(test_f.Forcemean)))
    
    meanangle=cmath.phase(test_f.Forcemean)

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(np.deg2rad(r),Testleg,color='r', label = "Quadriceps")
    ax.set_theta_direction(-1)
    ax.set_theta_offset(pi/2)
    plt.axvline(x=meanangle, color = "b")

    plt.show()

if(Testmode == 3):
    test_f = Force_state("TF")
    test_f_arm=Force_state("TFA")

    l= 12
    s= 2
    l_f=90
    s_f=10
    test_f.init_rollgaussian(length=l,sigma=s)
    test_f.init_rollgaussian_fatigue(l_f,s_f)

    test_f_arm.init_rollgaussian(length=l,sigma=s)
    test_f_arm.init_rollgaussian_fatigue(l_f,s_f)
    
    r = np.arange(0, 300, 1)
    Testforce_0 = np.empty([len(r)], dtype= complex)
    Testforce_2 = np.empty([len(r)], dtype=complex)
    Testforce_3 = np.empty([len(r)])
    Testforce_4 = np.empty([len(r)])
    Testforce_5 = np.empty([len(r)], dtype=complex)
    Testforce_6 = np.empty([len(r)])
    Testforce_7 = np.empty([len(r)])
    Testforce_8 = np.empty([len(r)])


    for i in range(len(r)):
        if(i<100):
            test_f.Forcemean=cmath.rect(randint(1,10),np.deg2rad(randint(80,110)))
            test_f_arm.Forcemean=cmath.rect(randint(1,5),np.deg2rad(randint(70,270)))
        elif(i<200):
            test_f.Forcemean=cmath.rect(randint(int(90-(i*0.2)),int(110-(i*0.2))),np.deg2rad(randint(60,70)))
            test_f_arm.Forcemean=cmath.rect(randint(45,55),np.deg2rad(randint(80,270)))
        else:
            test_f.Forcemean=cmath.rect(randint(int(40-i*0.1),int(60-i*0.1)),np.deg2rad(randint(70,90)))
            test_f_arm.Forcemean=cmath.rect(randint(10,40),np.deg2rad(randint(80,290)))

        
        test_f.move_rollgaussian()
        test_f.move_rollgaussian_fatigue()

        test_f_arm.move_rollgaussian()
        test_f_arm.move_rollgaussian_fatigue()
        

        Testforce_0[i]=(test_f.Forcemean)
        Testforce_2[i]=(test_f.rollgaussian)
        Testforce_3[i]= np.rad2deg(cmath.phase(test_f.Forcemean))
        Testforce_4[i]= np.rad2deg(cmath.phase(test_f.rollgaussian))

        Testforce_5[i]=(test_f.rollgaussian_fatigue)
        Testforce_6[i]= np.rad2deg(cmath.phase(test_f.Forcemean))
        Testforce_7[i]= np.rad2deg(cmath.phase(test_f.rollgaussian_fatigue))
        
        testratio_then = abs(test_f_arm.force_before_n_cycle)/abs(test_f.force_before_n_cycle)
        Testforce_8[i]= testratio_then[0]-testratio_then[-1]
        

    # Placing the plots in the plane
    plot1 = plt.figure(1)
    plot1 = plt.subplot2grid((3,3),(0,0),colspan = 3)
    plot2 = plt.subplot2grid((3,3),(1,0),colspan = 3)
    plot3 = plt.subplot2grid((3,3),(2,0),colspan = 3)
    
    plot1.plot(np.arange(0,l,1),np.flip(abs(test_f.g_factor)), 'g', label = "Gaussian Filter")
    plot1.set_title("one-sided Guassian Filter (discrete) [length, sigma]: "+str(l)+", "+str(s))
    plot1.set(xlabel="length of filter", ylabel= "weight")
    
    plot2.plot(r, abs(Testforce_0), 'r', label = "input signal") 
    plot2.plot(r, abs(Testforce_2), 'b', label = "output signal")
    plot2.set(xlabel="Nr. of cycles", ylabel= "Force [N]")
    plot2.legend(loc="upper left")

    plot3.plot(r,Testforce_3, 'r', label = "imput signal")
    plot3.plot(r,Testforce_4, 'b', label = "output signal")
    plot3.set(xlabel="Nr. of cycles", ylabel= "Angle [°]")
    plot3.legend(loc="lower left") 

    plt.subplots_adjust(hspace=1)

    plot4 = plt.figure(2)
    plot4 = plt.subplot2grid((4,3),(0,0),colspan = 3)
    plot5 = plt.subplot2grid((4,3),(1,0),colspan = 3)
    plot6 = plt.subplot2grid((4,3),(2,0),colspan = 3)
    plot7 = plt.subplot2grid((4,3),(3,0),colspan = 3)
    
    plot4.plot(np.arange(0,len(test_f.g_factor_fatigue),1),np.flip(abs(test_f.g_factor_fatigue)), 'g', label = "Gaussian Filter")
    plot4.set_title("one-sided Guassian Filter (discrete) [length, sigma]: "+ str(l_f)+", "+ str(s_f))
    plot4.set(xlabel="length of filter", ylabel= "weight")
    plot4.legend(loc="upper left")    

    
    plot5.plot(r, abs(Testforce_0), 'r', label = "input signal") 
    plot5.plot(r, abs(Testforce_5), 'b', label = "output signal")
    plot5.set(xlabel="Nr. of cycles", ylabel= "Force [N]")
    plot5.legend(loc="upper left")

    plot6.plot(r,Testforce_6, 'r', label = "imput signal")
    plot6.plot(r,Testforce_7, 'b', label = "output signal")
    plot6.set(xlabel="Nr. of cycles", ylabel= "Angle [°]")
    plot6.legend(loc="lower left") 

    plot7.plot(r,Testforce_8, 'r', label = "fatigue-ratio over filter length")
    plot7.set(xlabel="Nr. of cycles", ylabel= "ratio")
    plot7.legend(loc="upper left")

    plt.subplots_adjust(hspace=1)
    plt.show()

    
    
    
    
    






