import serial
from time import sleep
import io

import serial, time, io, datetime
from serial import Serial
addr = "COM8" ## serial port to read data from
baud = 9600 ## baud rate for instrument
serial_port = serial.Serial(
    port = addr,\
    baudrate = baud,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

# COMPORT = "8"
# # Open the serial port. The settings are set to Cisco default.
# serial_port = serial.Serial(COMPORT, baudrate=9600, timeout=None, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False)

# Make sure there is not any lingering input - input in this case being data waiting to be received
serial_port.flushInput()

print(serial_port.name)

serial_port.write("\n".encode())
# serial_port.write("?".encode())
# sio = io.TextIOWrapper(io.BufferedRWPair(serial_port, serial_port))
# sio.flush() # it is buffering. required to get the data out *now*
# hello = sio.readline()
# serial_port.write("root\n".encode())
#
# serial_port.write("mduadmin\n".encode())

bytes_to_read = serial_port.inWaiting()

# Give the line a small amount of time to receive data
sleep(.5)

# 9600 baud is not very fast so if you call serial_port.inWaiting() without sleeping at all it will likely just say
# 0 bytes. This loop sleeps 1 second each iteration and updates bytes_to_read. If serial_port.inWaiting() returns a
# higher value than what is in bytes_to_read we know that more data is still coming in. I noticed just by doing a ?
# command it had to iterate through the loop twice before all the data arrived.
while bytes_to_read < serial_port.inWaiting():
    bytes_to_read = serial_port.inWaiting()
    sleep(1)

# This line reads the amount of data specified by bytes_to_read in. The .decode converts it from a type of "bytes" to a
# string type, which we can then properly print.

data = serial_port.read(bytes_to_read).decode()
print(str(data))
print(str(data).find("User name"))
# TODO: have to analyze if login already based on the prompt. e.g. username
# serial_port.write("root\n".encode())
#
# serial_port.write("mduadmin\n".encode())

# This is an alternate way to read data. However it presents a problem in that it will block even after there is no more
# IO. I solved it using the loop above.
# for line in serial_port:
#     print(line)

# trying to login
# serial_port.write("root\n".encode())
#
# serial_port.write("mduadmin\n".encode())


# for line in serial_port:
#     print(line)


serial_port.close()