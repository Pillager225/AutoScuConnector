#!/usr/bin/env python3
from os import rename
from time import sleep
from subprocess import Popen, PIPE
from Emailer import sendemail

emailReciever = "owllvr@gmail.com"
emailSubject = "Raspberry Pi SCU Wifi Configuration"
credentialFile = "EmailBotPassword.psk"

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

def restartWifi():
    Popen(["ifdown", "wlan0"])
    Popen(["ifup", "wlan0"])
    # sleep to allow some time for DHCP server to provide an ip address
    sleep(5)

def getIP():
#    ifconfig = Popen(["ifconfig", "wlan0"], stdout=PIPE)
    ifconfig = Popen(["ifconfig", "enp30s0"], stdout=PIPE)
    ip = None
    out, err = ifconfig.communicate()
    out = str(out).split("\\n")
    for line in out:
        words = line.split()
        if len(words) > 0 and words[0] == "inet":
            ip = words[1]
    return ip

def getEmailCredentials():
    creds = f.open(credentialFile)
    i = 0
    emailSender = None
    emailPassword = None
    for line in creds:
        if i == 0:
            emailSender = line
        else if i == 1:
            emailPassword = line
        else:
            break
        i++
    return emailSender, emailPassword

def sendFailedEmail(ip):
    message = "The script could not connect to the wifi and get an ip address. The configuration has been reverted, and you may acess the system on the old wifi network at " + ip "\nThe reason for failure is unknown.\n"
    emailSender, emailPassword = getEmailCredentails()
    if emailSender != None and emailPassword != None:
        sendemail(emailSender, [emailReciever], [], emailSubject, message, emailSender, emailPassword)

def dealWithFailedConfig():
    # did not get an ip address for the network, so restore old wpa_supplicant.conf, so user can get back in
    rename(backup, filename)
    restartWifi()
    ip = getIP()
    if ip != None:
        sendFailedEmail(ip)

def acceptNetworkAgreement():
    pass

if __name__ == '__main__':
    filename = "wpa_supplicant.conf"
    backup = filename+".old"
    scuconfig = 'network={\n\tssid="ScuGuest"\n\tkey_mgmt=NONE\n}\n\n'
    reconfigureWPA(filename, backup, scuconfig)
    restartWifi()
    ip = getIP()
    if ip == None:
        dealWithFailedConfig()
    else:
        acceptNetworkAgreement()
