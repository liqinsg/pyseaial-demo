import serial
import io
ser = serial.serial_for_url('loop://5555', timeout=1)
# addr = "COM8" ## serial port to read data from
# baud = 9600 ## baud rate for instrument
# ser = serial.Serial(
#     port = addr,\
#     baudrate = baud,\
#     parity=serial.PARITY_NONE,\
#     stopbits=serial.STOPBITS_ONE,\
#     bytesize=serial.EIGHTBITS,\
#     timeout=0)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

sio.write(serial.unicode("display version\n"))
sio.flush() # it is buffering. required to get the data out *now*
hello = sio.readline()
print(hello == serial.unicode("display version\n"))