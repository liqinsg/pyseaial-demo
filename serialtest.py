import socket
import sys
import serial
ser = serial.Serial('COM8', 38400, timeout=1)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
while True:
    msg = ser.readline()
    sock.sendto(msg, ('localhost', 5555))
    sys.stdout.write(msg.decode())

