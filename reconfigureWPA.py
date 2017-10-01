#!/usr/bin/env python3
from os import rename
from time import sleep
from subprocesss import Popen, PIPE

def reconfigureWPA(filename, backup, newNetwork):
    inserted = False
    rename(filename, backup)
    with open(backup, "r") as old:
        with open(filename, "w") as new:
            for line in old:
                words = line.split()
                if  len(words) > 0 and not inserted and (words[0] == 'network' or words[0] == 'network=' or words[0] == 'network={'):
                    new.write(newNetwork)
                    inserted = True;
                new.write(line)
            new.close()
        old.close()

if __name__ == '__main__':
    filename = "wpa_supplicant.conf"
    backup = filename+".old"
    scuconfig = 'network={\n\tssid="ScuGuest"\n\tkey_mgmt=NONE\n}\n\n'
    reconfigureWPA(filename, backup, scuconfig)
    Popen(["ifdown", "wlan0"])
    Popen(["ifup", "wlan0"])
    sleep(5)
    ifconfig = Popen(["ifconfig", "wlan0"], stdout=PIPE)
    out, err = ifconfig.communciate()
    # TODO loop through output and find inet, email that to provided email address
    # after you accept the scu crap
