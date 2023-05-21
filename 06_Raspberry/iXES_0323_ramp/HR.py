from bleak import BleakScanner
import asyncio
import numpy as np
from PolarH10 import PolarH10

""" DHYB.py
Scan and connect to Polar H10 device
Retrieve basic sensor information including battery level and serial number
- Stream accelerometer data simultaneously with heart rate data
- Alternatively read sample data from a file
"""

async def record_HR(record_len, HR_label):
    
    devices = await BleakScanner.discover()
    polar_device_found = False

    for device in devices:
        if device.name is not None and "Polar" in device.name:
            polar_device_found = True
            polar_device = PolarH10(device)
            await polar_device.connect()
            await polar_device.get_device_info()
            await polar_device.print_device_info()

            await polar_device.start_hr_stream(HR_label)
            
            for i in range(record_len):
                await asyncio.sleep(1)

            await polar_device.stop_hr_stream()
            await polar_device.disconnect()
    
    if not polar_device_found:
        print("No Polar device found")
        HR_label.setText("X")

def save_sample_data(acc_data, ibi_data):
    np.savetxt("data/sample_data_acc.csv", np.column_stack((acc_data['times'], acc_data['values'])), delimiter=",")
    np.savetxt("data/sample_data_ibi.csv", np.column_stack((ibi_data['times'], ibi_data['values'])), delimiter=",")

if __name__ == "__main__":
    
    record_len = 20
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(record_HR(record_len))
