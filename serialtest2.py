from __future__ import print_function
import serial, time, io, datetime
from serial import Serial
addr = "COM8" ## serial port to read data from
baud = 9600 ## baud rate for instrument
ser = serial.Serial(
    port = addr,\
    baudrate = baud,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

print("Connected to: " + ser.portstr)
## this will store each line of data
seq = []
count = 1 ## row index
while True:
    for i in ser.read():
        seq.append(i) ## convert from ACSII?
        joined_seq = ''.join(str(v) for v in seq) ## Make a string from array

        if i == '\n':
            print("Line: " + str(count) + "" + str(datetime.datetime.now()) + joined_seq) ## append a timestamp to each row of data
            seq = []
            count += 1
            break

ser.close()

