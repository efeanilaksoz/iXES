from cgitb import reset
import math
from datetime import datetime
import time
from time import perf_counter
from tracemalloc import start

from matplotlib.pyplot import pause
from acquireSRMData import StopTime


"""readSRMData.py file converts binary data acquired from the SRM Xpower pedals to a text.file.
"""

StopTime = 20*60
#classes
class anti_corrupter:
    def __init__(self):            
        self.Timer = 0
        self.observer = False


def init_pedals_txt_file(file,name):
    """ Initialize txt dile for SRM X Power Pedals Data Aqcuisition """

    SRMrecordingVersion = 'Efe_Anil_Aksoz.v1'
    
    # File Info
    file.write('Version: ' + SRMrecordingVersion + '\n'
               'Processed Time: ' + datetime.today().strftime('%d.%m.%Y %H:%M:%S') +'\n'
               'Xpower pedal data' + '\n'
               'Recording ' + name + '\n'
               'fs: 30 Hz' + '\n'
               'Unit: force [N]' + '\n'
               '=================================' + '\n')

    # Header
    file.write('Timer\tcadenceCount\tAccRevTime\tAccTimeStamp\tFtan\tFrad\tFeff\tAngle\tAngularVelocity\tAmp\tLeftPlsw\tRightPlsw\n')

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is



def process_binfile(folder,filename):

    start = perf_counter()

    
    

    """Process binary data to txt data and write in the txt file"""
    txtname = folder + '/'+ filename + '.txt'
    #print('Txtname = ' + str(txtname))
    txtfile = open(txtname,'w')
    
    #print('Binfile = ' + str(folder + '/' + filename))
    binfile = open(folder + '/' + filename,'rb')
    
    
    init_pedals_txt_file(txtfile,txtname)

    bindata = binfile.read()
    data = [x for x in bindata]

    print('Reading binary file... Length is = ' + str(len(data)), end="\r")

    if(len(data)>0):
        
        count = 0
        i = 0
        cadenceCount_rev = data[i+4]
        pushback = 0
        imax = 0
        
        

        while i < len(data):
            #print("Reading binary file... Length is = ", len(data), "i = ", i)
            
                   


            Timer = int(str('{:08b}'.format(data[i+3])+
                            '{:08b}'.format(data[i+2])+
                            '{:08b}'.format(data[i+1])+
                            '{:08b}'.format(data[i])),2)

            Timer = Timer/1000



            cadenceCount = (data[i+4])-cadenceCount_rev
            cadenceCount='{:+3.0f}'.format(cadenceCount)

            AccRevTime = int(str('{:08b}'.format(data[i+6])+'{:08b}'.format(data[i+5])),2)/1024
            AccRevTime='{:4.2f}'.format(AccRevTime)

                
            
            count = data[i+7] # valid datasets
            limit= 9 # how many valid dataset can be processed by once

            #print(count)
            #time.sleep(0.01) # Sleep for 3 seconds
            
            safteybreak = i+count*12+32

            if safteybreak+33> len(data):
                break

            imax = max(i, imax) 

            if count>limit:

                i -= 31-(imax-i)
                #time.sleep(0.5) 
                count=0
               
    
            #if(Ant.observer == False):
            #    Ant.Timer = Timer
            #    Ant.Timer = float(Ant.Timer)
            #else:
            #    while(Ant.Timer+1< float(Timer)):
            #        i += 1
            #        safteybreak = i+count*12+32
            #        if safteybreak+33> len(data):
            #            break

               
                

            
            if count > 0 and count<limit:
                            
                        
                j =  i + 8



                #count = 6
            
                

                for k in range(0, (count-1)):
                    j = i+12*k
                    m = i+12*(count-1)

                    if(Timer < StopTime):

                        # Convert decimal data
                        AccTimeStamp = int(str('{:08b}'.format(data[j+11])+
                                            '{:08b}'.format(data[j+10])+
                                            '{:08b}'.format(data[j+9])+
                                            '{:08b}'.format(data[j+8])),2)/32768
                        AccTimeStamp='{:4.2f}'.format(AccTimeStamp)
                    

                        Ftan = twos_comp(int(str('{:+08b}'.format(data[j+13])+'{:08b}'.format(data[j+12])),2),16)/10
                        Frad = twos_comp(int(str('{:+08b}'.format(data[j+15])+'{:08b}'.format(data[j+14])),2),16)/10
                        Feff = round(math.sqrt(pow(Ftan,2)+pow(Frad,2)),5)
                        Ftan ='{:+4.2f}'.format(Ftan)
                        Frad ='{:+4.2f}'.format(Frad)
                        Feff ='{:3.5f}'.format(Feff)
                        Angle = int(str('{:08b}'.format(data[j+17])+'{:08b}'.format(data[j+16])),2)

                        if(Angle < 360 and Angle > 0):
                            AngularVelocity = abs(twos_comp(int(str('{:08b}'.format(data[j+19])+'{:08b}'.format(data[j+18])),2),16)/1024)
                            AngularVelocity='{:3.5f}'.format( AngularVelocity)

                            
                            Amp = int(str('{:08b}'.format(data[m+23])+'{:08b}'.format(data[m+22])+'{:08b}'.format(data[m+21])+'{:08b}'.format(data[m+20])),2)
                            Plsw_left = int(str('{:08b}'.format(data[m+27])+'{:08b}'.format(data[m+26])+'{:08b}'.format(data[m+25])+'{:08b}'.format(data[m+24])),2)
                            Plsw_right =int(str('{:08b}'.format(data[m+31])+'{:08b}'.format(data[m+30])+'{:08b}'.format(data[m+29])+'{:08b}'.format(data[m+28])),2)

                            if(Amp<130):
                                if(Plsw_left<505):
                                    if(Plsw_right < 505 ):  

                                        Timer = '{:4.3f}'.format(Timer)                                                        

                                        txtfile.write(str(Timer) + "\t" +
                                            str(cadenceCount) + "\t" +
                                            str(AccRevTime) + "\t" +
                                            str(AccTimeStamp) + "\t" +
                                            str(Ftan) + "\t" +
                                            str(Frad) + "\t" +
                                            str(Feff) + "\t" +
                                            str(Angle) + "\t" +
                                            str(AngularVelocity) + "\t" +
                                            str(Amp) + "\t" +
                                            str(Plsw_left) + "\t" +
                                            str(Plsw_right) + "\n"
                                            )

                                        Timer = float(Timer)
                                        pushback = 0
                                    else:
                                        i -= 1
                                        if(k != 0):
                                            k -= 1
                                        
                                else:
                                    i -= 1
                                    if(k != 0):
                                        k -= 1
                            else:
                                i -= 1
                                if(k != 0):
                                    k -= 1
                               
                        else:
                            i -= (k*8+1)+pushback
                            k = 0
                            if(k == 0 ):
                                i -= 1
                                pushback += 1
                                if (pushback > 10):
                                    i += 70
                           # print("secondary pushback, k = "+ str(k))

      
                    elif(pushback == 0):
                        i -= (k*8+1)
                        k = 0
                    else:
                        i -= (k*8+1)
                        k = 0
                        pushback +=1 
                        
                    

            i = i+count*12+32



            if i+33> len(data):
                reset()
                break
            else:
                pass
    
    txtfile.close()
    binfile.close()
