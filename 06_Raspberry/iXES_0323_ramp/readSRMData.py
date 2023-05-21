import math
from datetime import datetime
import time


"""readSRMData.py file converts binary data acquired from the SRM Xpower pedals to a text.file.
"""

def init_pedals_txt_file(file,name):
    """ Initialize txt dile for SRM X Power Pedals Data Aqcuisition """

    SRMrecordingVersion = 'marg-py.2021.v1'
    
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
    

    """Process binary data to txt data and write in the txt file"""
    txtname = folder + '/'+ filename + '.txt'
    txtfile = open(txtname,'w')
    binfile = open(folder + '/' + filename,'rb')
    
    init_pedals_txt_file(txtfile,txtname)

    bindata = binfile.read()
    data = [x for x in bindata]

    print("Reading binary file... Length is = ", len(data))

    i = 0

    while i < len(data):
        print("Reading binary file... Length is = ", len(data), "i = ", i)


        Timer = int(str('{:08b}'.format(data[i+3])+
                        '{:08b}'.format(data[i+2])+
                        '{:08b}'.format(data[i+1])+
                        '{:08b}'.format(data[i])),2)

        cadenceCount = data[i+4]

        AccRevTime = int(str('{:08b}'.format(data[i+6])+'{:08b}'.format(data[i+5])),2)/1024

        count = data[i+7]

        if count>10:
            count=0
            

        
        if count > 0 and count<10:
                        
                     
            j =  i + 8



            #count = 6
           
            

            for k in range(0, (count-1)):
                    j = i+12*k
                    m = i+12*(count-1)

                    # Convert decimal data
                    AccTimeStamp = int(str('{:08b}'.format(data[j+11])+
                                        '{:08b}'.format(data[j+10])+
                                        '{:08b}'.format(data[j+9])+
                                        '{:08b}'.format(data[j+8])),2)/32768
                    AccTimeStamp='{:3.2f}'.format(AccTimeStamp)
                

                    Ftan = twos_comp(int(str('{:+08b}'.format(data[j+13])+'{:08b}'.format(data[j+12])),2),16)/10
                    Frad = twos_comp(int(str('{:+08b}'.format(data[j+15])+'{:08b}'.format(data[j+14])),2),16)/10
                    Feff = round(math.sqrt(pow(Ftan,2)+pow(Frad,2)),5)
                    Ftan ='{:+3.2f}'.format(Ftan)
                    Frad ='{:+3.2f}'.format(Frad)
                    Feff ='{:3.5f}'.format(Feff)
                    Angle = int(str('{:08b}'.format(data[j+17])+'{:08b}'.format(data[j+16])),2)
                    AngularVelocity = abs(twos_comp(int(str('{:08b}'.format(data[j+19])+'{:08b}'.format(data[j+18])),2),16)/1024)
                    AngularVelocity='{:3.5f}'.format( AngularVelocity)
                    
                    Amp = int(str('{:08b}'.format(data[m+23])+'{:08b}'.format(data[m+22])+'{:08b}'.format(data[m+21])+'{:08b}'.format(data[m+20])),2)
                    Plsw_left = int(str('{:08b}'.format(data[m+27])+'{:08b}'.format(data[m+26])+'{:08b}'.format(data[m+25])+'{:08b}'.format(data[m+24])),2)
                    Plsw_right =int(str('{:08b}'.format(data[m+31])+'{:08b}'.format(data[m+30])+'{:08b}'.format(data[m+29])+'{:08b}'.format(data[m+28])),2)

                                            

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

            i = i+count*12+20



            if i+32 > len(data):
                break
            else:
                pass
    
    txtfile.close()
    binfile.close()
