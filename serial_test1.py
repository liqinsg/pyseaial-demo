__author__ = 'Tanner Ray Martin'

#this is for python 3, for python 2: change input to raw_input
import serial

#serial is the main module used and needs to be installed

import time

'''
I have a cisco 2960-s series switch hooked up to a laptop through a serial port so think of 'ser' as 'switch'
'''

#creating your serial object
# ser = serial.Serial(
#     port = 'COM8', #COM is on windows, linux is different
#     baudrate=9600, #many different baudrates are available
#     parity='N',    #no idea
#     stopbits=1,
#     bytesize=8,
#     timeout=8      #8 seconds seems to be a good timeout, may need to be increased
#     )
addr = "COM10" ## serial port to read data from
baud = 9600 ## baud rate for instrument
ser = serial.Serial(
    port = addr,\
    baudrate = baud,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)
#open your serial object
ser.isOpen()

#in this case it returns str COM3
print(ser.name)

#first command (hitting enter)
command = '\r\n'

#convert str to binary (commands sent to switch must be binary)
command = str.encode(command)

#send the command to the switch
ser.write(command)

#wait a sec
time.sleep(0.5)
ser.inWaiting()

#get the response from the switch
input_data = ser.read(225) #(how many bytes to limit to read)

#convert binary to str
input_data = input_data.decode("utf-8", "ignore")

#print response
print(input_data)

#create a loop
while 1:
    if input_data.find('User name:') == -1:
        print("may be login already or booting or something wrong")
        exit(100)
        #enter your own command
    command = input(':: ')

    #type 'exit' to end serial session with the switch
    if command == 'exit':
        ser.close()
        exit()
    
    else:
        #convert command to binary
        command = str.encode(command + '\r\n')
        #send command
        ser.write(command)
        time.sleep(2)
        input_data = ser.read(225)  # (how many bytes to limit to read)
        input_data = input_data.decode("utf-8", "ignore")
        # print response
        print(input_data)
        print(input_data.find('User password') != -1) # need input password?

        #set response variable (empty binary str)
        out = b''
        
        #take a short nap
        time.sleep(2)
        out.find('User name')
        #while response is happening (timeout hasnt expired)
        while ser.inWaiting() > 0:
            
            #trying to read one line at a time (100 bytes at a time)
            out = ser.readline(100)
            
            #converting response to str
            out = out.decode("utf-8", "ignore")

            #printing response if not empty
            if out != '':
                if out.find('User password') != -1:
                    print(out)
                    # pwd = 'mduadmin'
                    command = input(':: ')
                    command = str.encode(command + '\r\n')
                    ser.write(command)
                    # input_data = input_data.decode("utf-8", "ignore")
                    # # print response
                    # print(input_data)
                    out = b''
                    # take a short nap
                    time.sleep(2)
                elif out.find('The user has been locked') != -1:
                    print('The user has been locked. Please wait for 15 min and try again')
                elif out.find('prompt'):
                    print(out)
            #repeat until timeout