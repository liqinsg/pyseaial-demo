# https://semfionetworks.com/blog/establish-a-console-connection-within-a-python-script-with-pyserial/
import serial
from time import sleep

addr = "COM10"  ## serial port to read data from
baud = 9600  ## baud rate for instrument

isTest = True
cmd_fn = "ont_cmds_info.txt" if isTest else "ont_cmds_all.txt"
SHORT_SLEEP = 1
LONG_SLEEP5 = 5
LONG_SLEEP10 = 10
LONG_SLEEP30 = 30

cmdlist = ['display current-configuration']  # for testing
# get_cmds()
# print(cmdlist)


def get_output_data():
    # global output_data
    # get the response from the switch
    _output_data = ser.read(225)  # (how many bytes to limit to read)
    # convert binary to str
    _output_data = _output_data.decode("utf-8", "ignore")
    sleep(1)
    return _output_data


def send_to_console(ser: serial.Serial, command: str, wait_time: float = 0.5):
    command_to_send = command + "\r"
    ser.write(command_to_send.encode('utf-8'))
    sleep(wait_time)
    out = ser.read(ser.inWaiting()).decode('utf-8')
    list = out.split('\r\n')
    print(out, end="")
    return out, list[len(list) - 1]

"""
erase flash data
reboot system
"""
def command_type(cmd):
    entcmds = ["display current-configuration", "display version"]
    yescmds = ["port mode 0/0 gpon", "igmp mode snooping"]
    eraseflash = ["erase flash data","reboot system"]
    cmd = cmd.strip()
    cmd = cmd.rstrip("\n")
    if cmd.strip() in entcmds:
        return 1 # extra \n
    elif cmd in yescmds:
        return 2 # y
    elif cmd in '':
        return 3 # quit
    elif cmd in '':
        return 4 # need config
    elif cmd in eraseflash:
        return 100 # erase flash & reboot
    else:
        return 0


def wait_time(cmd):
    cmd = cmd.strip()
    cmd = cmd.rstrip("\n")
    cmds1 = ["display version"]
    cmds2 = ["display current-configuration"]
    if cmd in cmds1:
        return LONG_SLEEP5
    elif cmd in cmds2: #== "display current-configuration":
        return LONG_SLEEP30
    elif cmd == "":
        return SHORT_SLEEP
    else:
        return 0.5


def ext_cmd(cmd):
    if cmd == "display version":
        return 1 #'\r\n'
    elif cmd == "display current-configuration":
        return 2 #'y'
    elif cmd == "":
        return 3 #
    else:
        return 0

def get_cmds():
    global cmdlist
    with open(cmd_fn, 'r') as _file:
        _file.seek(0)
        cmdlist = _file.readlines()
    return cmdlist

get_cmds()

with serial.Serial(addr, timeout=1) as ser:
    print(f"Connecting to {ser.name}...")
    # nb_bytes_to_read = ser.inWaiting()
    # o = get_output_data()
    # print(o)
    # send_to_console(ser, "\r\n")
    # output_data = get_output_data()
    # print(o)

    while True:
        output_data, out = send_to_console(ser, "\r\n")
        # print(out.find('(config)#') == -1)
        # print(out) # TODO: mdu is >>User name or >>User password
        # print('----output data----')
        # print(len(output_data))
        # print(output_data)
        # if output_data == '':
        #     # it seems the mdu is ready. just enter
        #     send_to_console(ser, "\r\n")
        if len(out) > 0 and out[len(out) - 1] == '>':
            # it seems the mdu is login, enable
            send_to_console(ser, "enable")
            send_to_console(ser, "config")
            send_to_console(ser, "scroll\r\n")
            break
        elif len(out) > 1 and out[len(out) - 2:] == ')#' and out.find('(config)#') == -1:
            # it seems the mdu is enabled in privilege mode. will run commands
            send_to_console(ser, "quit\r\n")
        elif len(out) > 0 and out[len(out) - 1] == '#':
            # it seems the mdu is enabled in privilege mode. will run commands
            send_to_console(ser, "scroll\r\n")
            # print(out.find('(config)#') != -1)
            if out.find('(config)#') == -1:
                send_to_console(ser, "config")
            break
        elif len(out) > 2 and out[2:len(out) - 1] == 'User name':
            # it seems the mdu is enabled in privilege mode. will run commands
            send_to_console(ser, "root")
            send_to_console(ser, "mduadmin", wait_time=LONG_SLEEP5)
            send_to_console(ser, "\r\n")
            send_to_console(ser, "enable")
            send_to_console(ser, "\r\n")
            send_to_console(ser, "scroll\r\n")
            send_to_console(ser, "config")
            break
        elif len(out) > 2 and out[2:len(out) - 1] == 'User password':
            # it seems the mdu is enabled in privilege mode. will run commands
            send_to_console(ser, "mduadmin")
            send_to_console(ser, "enable")
            send_to_console(ser, "scroll\r\n")
            send_to_console(ser, "config")
            break
        # elif output_data == '':
        #     # it seems the mdu is ready. just enter
        #     send_to_console(ser, "\r\n")
        elif output_data == 'quit':
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
            send_to_console(ser, "\r\n")
        else:
            send_to_console(ser, "\r\n")
            # other prompt. actions depends but catch first
        sleep(0.5)

    for cmd in cmdlist:
        cmd = cmd.lstrip()
        cmd = cmd.lstrip("#")
        if cmd.strip() == '':
            continue
        # cmd += '\r\n'
        # TODO
        # inspect the cmd and add \r\n or y
        # 1,  ending with \r\n e.g. disp ver
        # 2,  ending with 'y', e.g. quit
        # 3, short sleep and long sleep
        # 4, need config
        # 5, interface config etc. both 4,5 need quit command
        type = command_type(cmd)
        wtime = wait_time(cmd)
        extcmd = ext_cmd(cmd)
        if type == 1:
            send_to_console(ser, cmd)
            out1, output = send_to_console(ser, '\r\n', wait_time=wtime)
            # out1 = str(out1).split('\r\n')
            # out2 = get_output_data()
            # print(out1)
            # print(out2)
        elif type == 2:
            send_to_console(ser, cmd.rstrip('\n'),wait_time=wtime)
            out1, output = send_to_console(ser, 'y')
        else:
            out1, output = send_to_console(ser, command=cmd, wait_time=wtime)
    # no need to quit out?
    if True:
        while output.find('(config)#') != -1:
            # it seems the mdu is enabled in privilege mode. will run commands
            out1, output = send_to_console(ser, "quit\r\n")
        send_to_console(ser, 'quit')  # logout
        send_to_console(ser, 'y')
    #
exit(0)

send_to_console(ser, 'quit')
send_to_console(ser, "mduadmin")
send_to_console(ser, "\r\n")
send_to_console(ser, "enable")
send_to_console(ser, "show ap summary", wait_time=2)
print(f"Connection to {ser.name} closed.")
