#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import json

isTest = True
cleaning = False
indent1 = ' '
indent2 = '  '

data_fn = "V-L7-C4-7112-ONT24.txt"


def get_ont_name(the_rx_dict, the_lines):
    match = get_matched(the_rx_dict, the_lines, 'ont_name')
    if match:
        return match.string.split('>')[0]
    return None


def get_matched(the_rx_dict, the_lines, the_key):
    for line in the_lines:
        key, match = parse_line(the_rx_dict, line)
        if key == the_key:
            return match
    return None


def parse_line(rx_dict, line):
    for key, rx in rx_dict.items():
        match = rx.search(line)
        if match:
            return key, match
    return None, None


def find_substring(line, substring_list=None, substring=None):
    if substring_list is not None:
        return any(map(line.__contains__, substring_list))
    elif substring is not None:
        return line.find(substring) != -1


class ONTDataClean_OVH:
    filepath = data_fn
    outputfilepath = 'command_list.json'
    lines = []
    rx_dict = {
        'ont_name': re.compile(r'^.*>')
    }

    def __init__(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath

    def parse_file(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath
        with open(self.filepath, 'r') as file_object:
            file_object.seek(0)
            self.lines = file_object.readlines()

        # TODO: incorrect
        ontnm = get_ont_name(self.rx_dict, self.lines)
        _ontnmkey = ontnm + '#'

        cmdlist = []  # output of the cmd list
        index = 0  # index of the lines list
        index, line, larr, indent = self.get_line(index)  # start to read line by line.
        sess_done = False
        while index < len(self.lines) - 1:
            # step 1 ending with #
            """
             ...
            [global-config]
              <global-config>
             sysname V-L2M-C2-2022-ONT29
             ... ?there's no indent for the next 2 lines?
             traffic table ip index 10 name "ip-traffic-table_10" cir 1024000 cbs 1024000 
            pir 1024000 pbs 1024000 color-mode color-blind priority 0 priority-policy 
            local-setting
             ...
            """
            if find_substring(str.strip(line), substring="[global-config]"):
                index += 2
                line = self.readline(index)
                cmd = {"cmd": line, "type": 0, "wtm": 0.5}
                cmdlist.append(cmd)
                while not self.ishax(line):
                    # index, line, larr, indent = self.get_line(index)
                    # if self.ishax(line):
                    #     break
                    if find_substring(line, substring="traffic table ip index"):
                        c1 = line
                        index += 1
                        c2 = self.readline(index)
                        index += 1
                        c3 = self.readline(index)
                        # merge the 3 lines
                        c = "{0} {1} {2}".format(c1.strip(), c2.strip(), c3.strip())
                        self.cmd_append(cmdlist, c)
                        # sess_done = True
                        break

                    index, line, larr, indent = self.get_line(index)
                print("step 1 completed")
            # step 2
            elif find_substring(str.strip(line), substring="[vlan-config]"):
                """
                [vlan-config]
                 vlan 12 to 13 smart
                 vlan 21 smart
                 vlan 72 to 73 smart
                 vlan 180 smart
                 ...
                 protocol-8021p-pri 5 vlan 13
                 port vlan 12 to 13 0/0 1
                 port vlan 21 0/0 1
                 port vlan 72 to 73 0/0 1
                 port vlan 180 0/0 1
                 #
                """
                self.cmd_append(cmdlist, "port mode 0/0 gpon")
                index, line, larr, indent = self.get_line(index)
                while not self.ishax(line):
                    # index, line = self.get_line(index)
                    # if self.ishax(line):
                    #     sess_done = True
                    #     break
                    if len(larr) <= 0:
                        continue
                    if larr[0] == "vlan":
                        self.split_lines_vlan(cmdlist, larr, line)
                    elif find_substring(line, substring="protocol"):
                        self.cmd_append(cmdlist, line)
                    elif larr[0] == "port":
                        self.split_lines_port(cmdlist, line)

                    index, line, larr, indent = self.get_line(index)
                print("step 2 completed")
            # step 3
            elif find_substring(str.strip(line), substring="[vlan-srvprof]"):
                """
                 vlan service-profile profile-id 10 profile-name "Chromecast"
                  packet-policy multicast forward
                  commit
                 vlan bind service-profile 2007 profile-id 10
                """
                index, line, larr, indent = self.get_line(index)
                while not self.ishax(line):
                    if len(larr) <= 0:
                        continue
                    if larr[0] == "vlan":
                        # TODO: should consider filter the 2 indent line
                        # and add quit at the end of the session
                        if larr[1] == "bind":
                            self.cmd_append(cmdlist, line)
                            break
                        self.cmd_append(cmdlist, line)
                        index, line, larr, indent = self.get_line(index)
                        # if self.ishax(line):
                        #     break
                        self.cmd_append(cmdlist, line, )
                        if larr[0] == "packet-policy":
                            index, line, larr, indent = self.get_line(index)
                            if larr[0] == "commit":
                                self.cmd_append(cmdlist, line, type=3)
                            else:
                                print("some thing wrong?")
                        else:
                            index, line, larr, indent = self.get_line(index)
                            if self.ishax(line):
                                break
                            self.cmd_append(cmdlist, line)

                    index, line, larr, indent = self.get_line(index)
                print("step 3 completed")
            # step 4
            elif str.strip(line) == "[eth]":  # find_substring(line, substring_list="[eth]"):
                index += 2
                line = self.readline(index)
                self.cmd_append(cmdlist, line)
                index += 1
                line = self.readline(index)
                self.cmd_append(cmdlist, line, type=3)
                print("step 4 completed")
            # step 5
            elif str.strip(line) == "[bbs-config]":  # find_substring(line, substring_list="[bbs-config]"):
                sess_done = False
                index += 2
                line = self.readline(index)
                self.cmd_append(cmdlist, line)
                index, line, larr, indent = self.get_line(index)
                while larr[0] == "service-port" and not self.ishax(line):
                    index0 = index
                    cmd = line
                    while 1:
                        index, line, larr, indent = self.get_line(index)
                        if str.strip(line) == '#':
                            break
                        if indent > 0:
                            break
                        # merge the line
                        cmd = "{0} {1}".format(cmd.strip(), line.strip())
                        index0 += 1
                    self.cmd_append(cmdlist, cmd)
                    index = index0
                    index, line, larr, indent = self.get_line(index)
                print("step 5 completed")
            # step 6
            elif str.strip(line) == "[btv-config]":  # find_substring(line, substring_list="[btv-config]"):
                index += 2
                line = self.readline(index)
                self.cmd_append(cmdlist, line)
                while not self.ishax(line):
                    if len(larr) <= 0:
                        continue
                    if larr[0] == "multicast-vlan":
                        self.cmd_append(cmdlist, cmd)
                    elif larr[0] == "igmp":
                        if larr[1] == "user" and larr[2] == "add":
                            self.cmd_append(cmdlist, line)
                        else:
                            self.cmd_append(cmdlist, line)
                    index, line, larr, indent = self.get_line(index)

                self.cmd_append(cmdlist, "quit")

                print("step 6 completed")
            # step 7
            elif str.strip(line) == "[prevlanif]":  # find_substring(line, substring_list="[prevlanif]"):
                while not self.ishax(line):
                    self.cmd_append(cmdlist, line, type=3)
                    index, line, larr, indent = self.get_line(index)
                print("step 7 completed")

            # increase the index and read next line
            index, line, larr, indent = self.get_line(index)

        with open(self.outputfilepath, "w") as FILE:
            json.dump(cmdlist, FILE)

        print("cmdlist all done")

    def split_lines_vlan(self, cmdlist, larr, line):
        if find_substring(line, substring="to"):  # seperate to 2+ lines
            i, j = int(larr[1]), int(larr[3])
            s = larr[len(larr) - 1]
            for k in range(i, j + 1):
                c = "{0} {1} {2}".format(larr[0], k, s)
                self.cmd_append(cmdlist, c)
        else:
            self.cmd_append(cmdlist, line)

    def split_lines_port(self, cmdlist, line):
        larr = line.split()
        if find_substring(line, substring="to"):  # seperate to 2+ lines
            i, j = int(larr[2]), int(larr[4])
            r = ' '.join(larr[5:])
            # s = larr[len(larr) - 1]
            for k in range(i, j + 1):
                c = "port vlan {0} {1}".format(k, r)
                self.cmd_append(cmdlist, c)
        else:
            self.cmd_append(cmdlist, line)

    def cmd_append(self, cmdlist, cmd: str = '\r\n', type=0, wtm: float = 0.5):
        cmdlist.append({"cmd": cmd, "type": type, "wtm": wtm})

    def ishax(self, line):
        b = len(line) > 0
        hax = line[0].find('#')
        return len(line) > 0 and not line[0].find('#') == -1

    def get_line(self, index):
        larr, indent = None, None
        index += 1
        line = self.readline(index)
        try:
            arr = line.split(' ')
            larr = line.split()
            indent = -1
            for s in line:
                indent += 1
                if s != ' ':
                    break
            # indent = 1: the first tier command
            # if indent > 1 or cmd == interface or some special cmd, need quit at end of the block
            # block ending: next indent == 1
            return index, line, larr, indent
        except:
            print("err1: ", index, line)
        finally:
            return index, line, larr, indent

    def readline(self, index):
        try:
            line = self.lines[index]
            return line
        except Exception as ex:
            return None


if __name__ == '__main__':
    ovhont = ONTDataClean_OVH(filepath=data_fn)
    ovhont.parse_file()
