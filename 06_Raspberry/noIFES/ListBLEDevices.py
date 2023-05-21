# Import libraries
import os                       
import asyncio                  
from bleak import BleakScanner
from bleak import BleakClient
#import pyttsx3 

# Clear Terminal
os.system('cls' if os.name == 'nt' else 'clear')

# Global Variables
FORCE_UUID = "7F510019-1B15-11E5-B60B-1697F925EC7B"     #From SRM XPower datasheet, notify firmware >= 14
BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"   

# Classes
class Xpower:
    def __init__(self, *args):            
        # Identifier 
        self.Id = args[0]
        self.Address = args[1]
        # Property related to Bleak
        self.Notifying = True

# define functions
async def DiscoverSensors():

    # Define local variables
    OtherDeviceNum = 0  #Set local variable for other BLE devices to keep the number
    SRMDeviceNum = 0    #SRM device number 

    print(">> Scanning BLE devices using BleakScanner")
    #engine = pyttsx3.init()
    #engine.say("Scanning BLE devices using BleakScanner")
    #engine.runAndWait()

    devices = await BleakScanner.discover(timeout=10) #This will scan for 5 seconds and produce a printed list of detected devices

    for d in devices:
        if "SRM_XP" in d.name:                                             #Check if SRM is in the name of the discovered sensor
            SRMDeviceNum = SRMDeviceNum + 1                             #Increase the SRM device number to keep track
            la = Xpower(d.name, d.address)
            print("\n",SRMDeviceNum,"SRM X-Power Sensor found:")
            print("====================================") 
            print("Name:\t\t", la.Id) 
            print("BLE Address:\t", la.Address, "(for MAC/Linux)")

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