iEES Go-Tryke Force
====================
the purpose of this python library is to acquire and record the SRM sensor data. 
Simultaneous connexion to the four sensors are made.
Data are recorded in binary files and then converted into txt files in the BLE folder.

Installation
-------------------------
Use Python 3.8 or later to run the algorithm.

Make sure to install all necessary imported library to run the program smoothly.
- Bleak, GDP_Client (available only by NR)
- asyncio, keyboard, platform, math, numpy, datetime, logging, argparse

Modify the X-Power sensors address in the function get_sensors 

Files
-------------------------
- run.py : include main event loops (record/get_battery) and run options
- params.py : Start-up parameters. Include BLE characteristics address, ref time and binary filenames
- acquireSRMData.py : include all Classes, Async functions to communicate with SRM sensors pedals
- readSRMData.py : initiialize the txt file of recorded sensors data, process the binary data to txt data, build the txt file in the specified folder.

Usage
-------------------------
To run the different programs use the following commands. 

```
# record sensor_data
python run.py record

To end the program, use the canceller token :(keypress command = 'e')

# Get battery of sensor data
python run.py get_battery
```
