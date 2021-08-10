__author__ = 'Tanner Ray Martin'
#https://gist.githubusercontent.com/TannerRayMartin/f0b91c5e492b1f15698656486403ef02/raw/e48ce226cc98e5e0adf7b23e737fbf6e1bc7d4ea/serial_test1.py
# this is for python 3, for python 2: change input to raw_input
import serial

# serial is the main module used and needs to be installed

import time


def byte2str(output_data):
    inp = output_data.decode()
    return inp


'''
I have a cisco 2960-s series switch hooked up to a laptop through a serial port so think of 'ser' as 'switch'
'''

# creating your serial object
ser = serial.Serial(
    port='COM10',  # COM is on windows, linux is different
    baudrate=9600,  # many different baudrates are available
    parity='N',  # no idea
    stopbits=1,
    bytesize=8,
    timeout=8  # 8 seconds seems to be a good timeout, may need to be increased
)

# open your serial object
ser.isOpen()
# returns str COM#
print(ser.name)
# # send the command to the switch
# ser.write(command)
#
# # wait a sec
# time.sleep(0.5)
# ser.inWaiting()


def get_output_data():
    # global output_data
    # get the response from the switch
    _output_data = ser.read(225)  # (how many bytes to limit to read)
    # convert binary to str
    _output_data = _output_data.decode("utf-8", "ignore")
    time.sleep(1)
    return _output_data


def serial_write(command):
    # global command
    # command = str.encode(command + '\r\n')
    ser.write(command)
    time.sleep(.5)
    ser.inWaiting()
    return get_output_data()

print(get_output_data())

# first command (hitting enter)
command = '\r\n'
# convert str to binary (commands sent to switch must be binary)
command = str.encode(command)
output_data = serial_write(command)


def enter_cmd():
    # global command, enter, output_data
    command = '\r\n'
    enter = str.encode(command)
    return serial_write(enter)


# insp = byte2str(output_data)
# print response
# print(output_data)
# there're 3 cases:
## 1, prompt to login
## 2, account locked
## 3, login already
while True:
    print('----output data----')
    print(output_data)
    print(len(output_data))
    if output_data == '':
        # it seems the mdu is ready. just enter
        ser.write(str.encode("\r\n"))
    if output_data == 'quit':
        # just enter
        ser.write(str.encode("y\r\n"))
        break
    elif output_data.find('The user has been locked') > -1:
        # another enter to get login prompt
        print('The user has been locked, exit and wait for a while')
        exit(100)
    elif output_data.find('please press any key to log on') > -1:
        # another enter to get login prompt
        # ser.write(str.encode("\r\n"))
        # command = '\r\n'
        # enter = str.encode(command)
        # output_data = serial_write(enter)
        output_data = enter_cmd()
        continue
    elif output_data.find('User name:') > len(output_data) - 11:
        # enter username
        # command = input(':: ')
        command = 'root'
        command += '\r\n'
        command += 'mduadmin'
        command += '\r\n'

        command = str.encode(command)
        output_data = serial_write(command)
        continue
        # ser.write(str.encode("root\r\n"))
    elif output_data.find('User password:') > -1:
        print(output_data)
        # enter password
        command = input(':: ')
        password = str.encode(command)
        output_data = serial_write(password)
        continue
        # ser.write(str.encode("mduadmin\r\n"))
    else:
        output_data = enter_cmd()
        # other prompt. actions depends but catch first
        pass

# create a loop
while True:
    # enter your own command
    command = input(':: ')

    # type 'exit' to end serial session with the switch
    if command == 'exit':
        ser.close()
        exit()
    elif output_data.find('User name') > 10:
        print(output_data.find('User name'))
        serial_write()
        out = ser.readline(100)
        out = out.decode("utf-8", "ignore")
        continue
    elif output_data.find('Username or password invalid') != -1:
        command = str.encode('\r\n')
        ser.write(command)
        time.sleep(.5)
        continue
    else:
        # convert command to binary
        command = str.encode(command + '\r\n')

        # send command
        ser.write(command)

        # set response variable (empty binary str)
        out = b''

        # take a short nap
        time.sleep(.5)

        # while response is happening (timeout hasnt expired)
        while ser.inWaiting() > 0:

            # trying to read one line at a time (100 bytes at a time)
            out = ser.readline(100)

            # converting response to str
            out = out.decode("utf-8", "ignore")

            # printing response if not empty
            if out != '':
                print(out)

            # repeat until timeout


