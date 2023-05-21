# List available BLE devices, look for SRM X-Power Sensors and read the battery level if found 
# Created on: 11.01.22 by ase1@bfh.ch
# Editted on: 22.02.22 by ase1@bfh.ch
# Last update notes: Bleak doesn't work with MAC0S 12.0, 12.1 and 12.2. Issue resolved with 12.3 beta

# Import libraries
import os                       #Operation System library to clear terminal
import asyncio                  #Asynchronous I/O library to write concurrent code using the async/await syntax.
from bleak import BleakScanner  #Bluetooth Low Energy platform Agnostic Klient (Bleak) Bleak is a GATT client software, capable of connecting to BLE devices acting as GATT servers.
from bleak import BleakClient   #Bleak client used for connecting the BLE device

# Clear Terminal
os.system('cls' if os.name == 'nt' else 'clear')

# from setuptools import setup

# Global Variables
FORCE_UUID = "7F510019-1B15-11E5-B60B-1697F925EC7B"     #From SRM XPower datasheet, notify firmware >= 14
BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"   #From SRM XPower datasheet
SRM_BiPED_Arm_Left = "SRM_XP_L_1828"
SRM_BiPED_Arm_Right = "BROKEN"
SRM_BiPED_Leg_Left = "SRM_XP_L_1691"
SRM_BiPED_Leg_Right = "SRM_XP_R_1462"
SRMSensorNames = [SRM_BiPED_Arm_Left, SRM_BiPED_Arm_Right, SRM_BiPED_Leg_Left, SRM_BiPED_Leg_Right]

# Go-Tryke SRM Sensors LEG
# B07FB322-8A99-4664-8B23-2EDDBAF7CF3E: SRM_XP_L_1633 - LL - Windows: DFFCB858E9BF
# ECCBA022-5795-461F-86BE-57E063AAF84A: SRM_XP_R_1556 - RL - Windows: D1BC2A90A931

# Go-Tryke SRM Sensors ARM
# 0DEC8817-1B6A-4689-93C6-7E060BDD52D4: SRM_XP_L_1690 - LA - Windows: CE26BE9A5CE5
# 8BEC40A0-BE54-4544-A120-D5BEC63E412B: SRM_XP_R_1425 - RA - Windows: D6371E3E733C

# 51F70C83-11E2-9B57-D13D-BB61E13853CB: SRM_XP_L_1691
# EA78D6CA-EC75-8DF6-38CC-3298713BF5BA: SRM_XP_R_1462

# Classes
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

# define functions
async def DiscoverSensors():

    # Define local variables
    OtherDeviceNum = 0  #Set local variable for other BLE devices to keep the number
    SRMDeviceNum = 0    #SRM device number 

    print(">> Scanning BLE devices using BleakScanner")  
    devices = await BleakScanner.discover(timeout=10) #This will scan for 5 seconds and produce a printed list of detected devices

    for d in devices:
        if "SRM_XP" in d.name:                                             #Check if SRM is in the name of the discovered sensor
            SRMDeviceNum = SRMDeviceNum + 1                             #Increase the SRM device number to keep track
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
        else:                                                           #If SRM is not the name: Give info about the BLE scanner results
            OtherDeviceNum = OtherDeviceNum+1                           #Just increase the other device number for result

    if SRMDeviceNum is 0:
        print(">>",OtherDeviceNum ,"other devices were found, but none of them are SRM sensor.\nPlease check if they are ON and try again!")
    else:
        print(">>",OtherDeviceNum ,"other devices were found...")

# Program actually starts here:
asyncio.run(DiscoverSensors())