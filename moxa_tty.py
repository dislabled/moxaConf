#!/usr/bin/env python3
# coding=utf-8

from moxalib import Connection
#import time

def make_alarmdict(ifacelist, alarmlist, clientport):
    """
    Makes a dictionary of ports with alarm on and off
    ----- DEPRECATED ----
    args:   ifacelist (list) - status of interfaces
            alarmlist (list) - interfaces with alarm
            clientport (int) - port  which the client is attached to

    returns: alarmdict (dict) - 
    """
    alarmdict = {}
    for i in range(len(ifacelist)):
        if i != int(clientport) -1:
            if ifacelist[i] == 'Up' and alarmlist[i] != 'Off':
                alarmdict[i+1] = 1
            elif ifacelist[i] == 'Down' and alarmlist[i] == 'Off':
                alarmdict[i+1] = 0
        else:
            alarmdict[i+1] = 0
    alarmdict[7] = 1
    alarmdict[8] = 1
    return alarmdict


def parse_list(list, keyword) -> list:
    """
    Parses the port/or alarmlist(list). (keyword) triggers on.
    Returns a list of active in list
    """
    cnt = 1
    ports = []
    for port in list:
        if port == keyword:
            ports.append(1)
        else:
            ports.append(0)
        cnt += 1
    return ports
#
# def parse_list(list, keyword):
#     """
#     Parses the port/or alarmlist(list). (keyword) triggers on.
#     Returns a list of active in list
#     """
#     cnt = 1
#     ports = []
#     for port in list:
#         if port == keyword:
#             ports.append(cnt)
#         cnt += 1
#     return ports

def check_list(list:list, match:str) -> int:
    val = -1
    cnt = 0
    for row in list:
        if match.rstrip('MR') == row[0]:
            val = cnt
        cnt += 1
    return val

def versiontup(version):
    return tuple(map(int, (version.split("."))))


if __name__ == "__main__":
    # while True:
        # try:
        #     moxa_switch = Connection()
        # except:
        #     print('Cannot open connection')
        #     quit(1)
        #
        # logincheck = moxa_switch.check_login()
        # if logincheck == 0:
        #     moxa_switch.menu_login()
        #     continue
        # elif logincheck == 1:
        #     moxa_switch.cli_login()
        #     print(moxa_switch.get_sysinfo())
        #     print(moxa_switch.get_version())
        #     print(moxa_switch.get_ifaces())
        #     print(moxa_switch.get_portconfig())
        #     print(moxa_switch.get_ip()) 
        #     # if input('fw?').upper() != 'Y':
        #     #     print(moxa_switch.copy_firmware('/home/stian/Projects/moxaParse/EDS408A_V3.8.rom'))
        #     # moxa_switch.conf_ip('192.168.127.253')
        #     input('done.')
        #     quit(-1)
        # else:
        #     print('Cannot log in: ', + logincheck)
        #     input('done.')
        #     quit(2)

    moxa_switch = Connection()
    moxa_switch.check_login()
    moxa_switch.cli_login()
    # system = moxa_switch.get_sysinfo()
    # version = moxa_switch.get_version()
    # alintports = parse_list(moxa_switch.get_portconfig(), 'Off')
    # stintports = parse_list(moxa_switch.get_ifaces(), 'Up')
    # mgmt_ip = moxa_switch.get_ip()
    print(moxa_switch.get_eventlog())
    input()
    # print(system)
    # print(version)
    # print(moxa_switch.get_portconfig())
    # print(alintports)
    # print(moxa_switch.get_ifaces())
    # print(stintports)
    # print(mgmt_ip)O

    # system = ['Managed Redundant Switch 06113', 'Switch Location', 'EDS-408A-MM-SC', '', '00:90:E8:73:46:55', '0d1h50m58s']
    # version = ['EDS-408A-MM-SC', 'V3.8']
    # alintports = parse_list(['Ignore', 'Ignore', 'Ignore', 'Off', 'Ignore', 'Ignore', 'Ignore', 'Ignore'], 'Off')
    # stintports = parse_list(['Down', 'Down', 'Up', 'Down', 'Down', 'Down', 'Down', 'Down'], 'Up')
    # mgmt_ip = ['1', 'Static', '192.168.127.253', '255.255.255.0', '0.0.0.0', '', '', '::', 'fe80::290:e8ff:fe73:4655']
    # print(alintports)
    # print(stintports)
    # gui = Gui_MainWindow(system, version, alintports, stintports, mgmt_ip)
    # gui.main()

