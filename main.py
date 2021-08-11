import json

from mdu_config_clone import mdu_config
from mdu_health_clean import ONTDataClean_OVH

if __name__ == '__main__':
    # erase the system or not
    isErase = True
    # the file name of the mdu
    data_fn = "V-L7-C4-7112-ONT24.txt"

    ovhont = ONTDataClean_OVH(filepath=data_fn)
    # save to the json file
    command_list_fn = data_fn[:len(data_fn) - 3] + "json"
    cmdlist = ovhont.parse_file()
    with open(command_list_fn, "w") as FILE:
        json.dump(cmdlist, FILE)

    # COM port
    addr = "COM10"
    print("erase flash")
    erase_ok = mdu_config(erase=isErase, cmd_fn=command_list_fn)
    if isErase and erase_ok:
        print("clone the configuration")
        cmd_fn_json = command_list_fn
        mdu_config(erase=False, cmd_fn=command_list_fn)

