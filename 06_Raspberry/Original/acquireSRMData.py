import asyncio
import keyboard
import platform
import math
import numpy as np

from time import time

from bleak import BleakClient

from params import *
from readSRMData import *

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
            if keyboard.is_pressed('e') and self.Cancelled == False:
                self.Cancelled = True
                break
            await asyncio.sleep(2) # ms loop every 2000ms

# FUNCTIONS*************************************************************************
def get_sensors(folder='none',fake=False):
    # SRM X power pedals  addresses
    """
    "SRM_XP_L_1828"    "6575BCF5-BA89-471F-A8F9-E0FD7FDED200"    -62     [1×1 struct] 
    "SRM_XP_L_1691"    "0A9A867D-2DC4-4013-A026-98ACDE06877F"    -74     [1×1 struct] 
    "SRM_XP_R_1462"    "309D2B29-350D-40DE-ACE3-C879907EA5B0"    -72     [1×1 struct] 
    """
    if fake:
        # FAKE SENSOR
        adress = '05647B2D-C327-48D4-8763-FB3A35C8A293'
        phone = Xpower("phone", adress)
        sensors = [phone]
    else:    
        ll_addr = ("DF:FC:B8:58:E9:BF" # for Windows/Linux System
                    if platform.system() != "Darwin"
                    else '0A9A867D-2DC4-4013-A026-98ACDE06877F' # for MAC OS System
                    )
        rl_addr = ("D1:BC:2A:90:A9:31" # for Windows/Linux System
                    if platform.system() != "Darwin"
                    else 'ECCBA022-5795-461F-86BE-57E063AAF84A' # for MAC OS System
                    )
        la_addr = ("CE:26:BE:9A:5C:E5" # for Windows/Linux System
                    if platform.system() != "Darwin"
                    else '0DEC8817-1B6A-4689-93C6-7E060BDD52D4' # for MAC OS System
                    )
        ra_addr = ("D6:37:1E:3E:73:3C" # for Windows/Linux System
                    if platform.system() != "Darwin"
                    else '8BEC40A0-BE54-4544-A120-D5BEC63E412B' # for MAC OS System
                    )

        ll = Xpower("ll", ll_addr,folder)
        rl = Xpower("rl", rl_addr,folder)
        la = Xpower("la", la_addr,folder)
        ra = Xpower("ra", ra_addr,folder)
        #sensors = [ll, rl, la, ra]

    return ll #rl, la, ra
               
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

    disconnected_event = asyncio.Event()
    notifying_event = asyncio.Event()

    # NOTIF CALLBACK *******************
    def callback(sender, data): # the whole callback takes 0.08ms to write binfile
        if not sensor.Notifying: 
            log.info(f"Sensor {sensor.Id} begins notify at {int((time()-REF_TIME)*1000)} ms")
            sensor.Notifying = True
            notifying_event.set()
        else:
            # Write in File
            timestamp = int((time()-REF_TIME)*1000)
            sensor.SaveByte.write_in_file(timestamp.to_bytes(4, byteorder='little', signed=False))
            sensor.SaveByte.write_in_file(data)
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
                sensor.Address, disconnected_callback = disconnected_callback,timeout=20.0,use_cached = False
            ) as client:
                
                if client.is_connected:
                    log.info(f"Sensor {sensor.Id} is connected")
                    # ********************************************
                    # Record
                    try:
                        # Wait for notification (if none, enter except)
                        await client.start_notify(FORCE_UUID, callback)
                        await asyncio.wait_for(notifying_event.wait(),3)

                        # Wait for a potential unsolliciated disconnection or keypress event
                        await asyncio.wait({canceller_token.check_ui_cancel(log), disconnected_event.wait()}, return_when=asyncio.FIRST_COMPLETED)

                        if canceller_token.Cancelled:
                            await client.stop_notify(FORCE_UUID)
                            await client.disconnect()
                            if not client.is_connected:
                                log.info(f"End of recording: Sensor {sensor.Id} got disconnected properly")
                        else:
                            disconnected_event.clear()

                    except:
                        await client.stop_notify(FORCE_UUID)
                        await client.disconnect()
                        if not sensor.Notifying:
                            log.warning(f"Cannot notify sensor {sensor.Id}. Retrying...")
                    # ********************************************
        except: # log warning
            log.error(f"Cannot (re)connect to sensor {sensor.Id}. Retrying...")

    # Close Binary File
    sensor.SaveByte.stop()