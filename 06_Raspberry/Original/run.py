import asyncio
import logging
import argparse
import os
import errno
from acquireSRMData import *
from params import *
from datetime import datetime

""" This file runs the program IEES GO-Tryke Force. You can either record/stimulate/get_battery."""

def main():
    
    args = options()
    
    if args.action !='get_battery':
        # Build Folder to store Session Data 
        process_time = datetime.today().strftime('%Y%m%d%H%M%S')
        folder = '../BLE/' + process_time
        try:
            os.makedirs(folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    if args.action == "record":
        run_record(folder)
    
    elif args.action =='get_battery':
        run_get_battery()
     
    address='0A9A867D-2DC4-4013-A026-98ACDE06877F'
       
    loop_battery = asyncio.get_event_loop()
    battery_task = get_battery(address)
    loop_battery.run_until_complete(battery_task)

def options():
    parser = argparse.ArgumentParser(description='************* IEES GO-Tryke *************')
    parser.add_argument('action', choices=['record','get_battery'],type=str, default='record', help='Choose your program: ')
    args = parser.parse_args()
        
    return args

#***********************************************************************************************************
def run_record(folder,debug=True):
    # Initialize Logger
    log = logging.getLogger(__name__)
    if debug:
        log.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        fh = logging.FileHandler(folder + '/GO_Tryke_Streamer.txt')
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
    sensors = get_sensors(folder=folder)
    
    # Initialize Canceller Token
    canceller_token = CancellerToken()

    # Record Data & Store in Binfile ***********************************
    loop = asyncio.get_event_loop()
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
        process_binfile(folder,binfile)
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

##############################       
if __name__ == "__main__":  ##
    main()                  ##
##############################