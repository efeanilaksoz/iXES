import serial
import os

# Clear Terminal
os.system('cls' if os.name == 'nt' else 'clear')

RehaStim = serial.Serial('/dev/tty.usbserial-HMSIWVLN', 11520, timeout=5, parity='N', stopbits=2, bytesize=8, rtscts=0)  # open serial port
print(RehaStim.name, "Connected & Listening...")         # check which port was really used
answer = RehaStim.read()
print("Received:", answer)
RehaStim.write(bytes.fromhex('E2 21 48 78'))          # write a hex code and send it in Binary
print(RehaStim.name, "Command sent...")         # check which port was really used
answer = RehaStim.read() 
print("Received:", answer)
RehaStim.close()
print(RehaStim.name, "disconnected...")         # check which port was really used