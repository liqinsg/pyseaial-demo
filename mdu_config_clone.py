import json
from time import sleep

import serial

#
# TODO: merge telnet and console port
#

addr = "COM10"  ## serial port to read data from

isTest = True
isErase = False

cmd_fn_json = "V-L3-C4-3131-ONT16.json"
SHORT_SLEEP = 1
LONG_SLEEP5 = 5
LONG_SLEEP10 = 10
LONG_SLEEP30 = 30

cmdlist = ['display current-configuration']  # for testing


def send_to_console(ser: serial.Serial, command: str, wait_time: float = 0.5):
    command_to_send = command + "\r"
    ser.write(command_to_send.encode('utf-8'))
    sleep(wait_time)
    out = ser.read(ser.inWaiting()).decode('utf-8')
    list = out.split('\r\n')
    print(out, end="")
    return out, list[len(list) - 1]


def get_cmds_json(cmd_fn=cmd_fn_json):
    global cmdlist_json
    with open(cmd_fn) as f:
        cmdlist_json = json.load(f)
    # sort json
    cmdlist_json = sorted(cmdlist_json, key=lambda k: k['index'], reverse=False)
    return cmdlist_json


def mdu_config(erase=False, cmd_fn=cmd_fn_json):
    with serial.Serial(addr, timeout=1) as ser:
        print(f"Connecting to {ser.name}...")
        while True:
            output_data, out = send_to_console(ser, "\r\n")
            k = out[2:len(out) - 1] if len(out) > 2 else None
            j = out[len(out) - 1] if len(out) > 1 else None
            if len(out) < 1:
                send_to_console(ser, "\r\n")
            elif j == '>':
                # it seems the mdu is login, enable
                send_to_console(ser, "enable")
                send_to_console(ser, "config")
                send_to_console(ser, "scroll\r\n")
                break
            elif out[len(out) - 2:] == ')#' and out.find('(config)#') == -1:
                # it seems the mdu is enabled in privilege mode. will run commands
                send_to_console(ser, "quit\r\n")
            elif out[len(out) - 1] == '#':
                # it seems the mdu is enabled in privilege mode. will run commands
                send_to_console(ser, "scroll\r\n")
                if out.find('(config)#') == -1:
                    send_to_console(ser, "config")
                break
            elif k == 'User name':
                # it seems the mdu is enabled in privilege mode. will run commands
                send_to_console(ser, "root")
                send_to_console(ser, "mduadmin", wait_time=LONG_SLEEP5)
                send_to_console(ser, "\r\n")
                send_to_console(ser, "enable")
                send_to_console(ser, "\r\n")
                send_to_console(ser, "scroll\r\n")
                send_to_console(ser, "config")
                break
            elif k == 'User password':
                # it seems the mdu is enabled in privilege mode. will run commands
                send_to_console(ser, "mduadmin")
                send_to_console(ser, "enable")
                send_to_console(ser, "scroll\r\n")
                send_to_console(ser, "config")
                break
            elif output_data == 'quit':
                # just enter
                ser.write(str.encode("y\r\n"))
                break
            elif output_data.find('The user has been locked') > -1:
                # another enter to get login prompt
                print('The user has been locked, exit and wait for a while')
                exit(10)
            elif output_data.find('please press any key to log on') > -1:
                send_to_console(ser, "\r\n")
            else:
                send_to_console(ser, "\r\n")
                # other prompt. actions depends but catch first
            sleep(0.5)

        """
        erase flash data
        reboot system
        """
        if erase:
            try:
                send_to_console(ser, "erase flash data")
                send_to_console(ser, "y")
                send_to_console(ser, "\r\n")
                send_to_console(ser, "reboot system")
                send_to_console(ser, "y")
                send_to_console(ser, "\r\n")
                print("system erased. it takes 2 min to complete.....")
                sleep(2 * 60)
                return True
            except:
                print("erase failure")
                return False

        # continue with commands
        get_cmds_json(cmd_fn)
        cmdlist = cmdlist_json
        """
        cmd type 0: normal, 1:  <cr> to continue, 2: y to confirm, 3: quit back to pre-tier
        """
        for cmd_json in cmdlist:
            cmd = cmd_json["cmd"].lstrip()
            if str.strip(cmd) == "poe 1 max-power 30000":
                print(cmd)
            type = cmd_json["type"]
            wtime = cmd_json["wtm"]
            if cmd.find("service-port 0 vlan 2007 eth 0/1/1 multi-service") != -1:
                print(cmd)
            if type == 1:
                send_to_console(ser, cmd)
                out1, output = send_to_console(ser, '\r\n', wait_time=wtime)
            elif type == 2:
                send_to_console(ser, cmd.rstrip('\n'), wait_time=wtime)
                out1, output = send_to_console(ser, 'y')
            elif type == 3:
                send_to_console(ser, cmd.rstrip('\n'), wait_time=wtime)
                out1, output = send_to_console(ser, 'quit\r\n')
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


if __name__ == '__main__':
    mdu_config(erase=isErase)
