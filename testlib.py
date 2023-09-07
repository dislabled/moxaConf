#!/usr/bin/python3
from xmodem import XMODEM, NAK
from ipaddress import ip_address
from time import sleep

# TODO: 
# set time : configure -> clock set hh:mm:ss month day year

class Connection:
    """
    Function on a serial object for moxa EDS routers
    """

    def __init__(self, device:str='/dev/ttyUSB0', baud:int=115200, timeout:int=1,
            prompt:bytes=b'EDS-408A-MM-SC', xonxoff:int=1, verbose:bool=False) -> None:
        self.device = device
        self.baud = baud
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.verbose = verbose
        self.p_end = b'#'
        self.prompt = prompt + self.p_end
        self.cprompt = prompt + b'(config)' + self.p_end
        self.iprompt = prompt + b'(config-if)' + self.p_end
        self.vprompt = prompt + b'(config-vlan)' + self.p_end
        # self.ser = Serial(port=self.device, baudrate=self.baud, timeout=self.timeout, xonxoff=self.xonxoff)
        self.total_packets = 0
        self.success_count = 0
        self.error_count = 0
        

    def vprint(self, text) -> None:
        """
        Prints only when verbose is true
        """
        if self.verbose == True:
            print(f'Moxalib: {text}')

    def reset_conn(self) -> None:
        """ Reset Connection
        """
        pass

    def expect(self, buffer:list, wtf:list) -> int:
        """ find a string in read value

        Args:
            wtf (str): what to find

        Returns:
            int: -1 if nothing found, stringindex for match,
                 -2 if empty buffer
        """
        findval = buffer[-1]
        for i, b in enumerate(wtf): # Using enumerate for now, hack for bytes object
            _ = b
            if findval.find(wtf[i]) != -1:
                return(i)
        return(-1)

    def check_login(self):
            """ Checks if login mode is menu or cli

            Returns:
                    (0 is menu, 1 is cli, -1 when nothing matched)
            """
            return_val = 1
            self.vprint(f'check_login function: {return_val}')
            return return_val
            # return returnval

    def menu_login(self, user:str='admin', password:str='') -> None:
        """ Login with menu, and change to cli login

        Args: 
            user (str): username, default 'admin'
            password (str): password, default ''
        """
        self.vprint('Writing Account name: {}'.format(user))
        self.vprint('Writing Password: {}'.format(password))


    def cli_login(self, user:str='admin', password:str='') -> None:
        """ Login with cli login

        Args: 
            user (str): username, default 'admin'
            password (str): password, default ''
        """
        self.vprint('Writing Account name: {}'.format(user))
        self.vprint('Writing Password: {}'.format(password))


    def keepalive(self) -> int:
        """ Keeps user logged in
        
        Returns:
            int: -1: OK
                  0: Error
        """
        self.vprint('keepalive function: -1')
        return -1




    def get_sysinfo(self) -> list:
        """ Gets system info and returns it as a list

        Returns:
            list: System parameters
                  0: System Name, 1: Switch Location,
                  2: Switch Description, 3: Maintainer Info,
                  4: MAC Address, 5: Switch Uptime
        """
        return_list = ['Managed Redundant Switch 06113', 'Switch Location', 'EDS-408A-MM-SC', '', '00:90:E8:73:46:55', '0d0h40m48s']
        self.vprint(f'get_sysinfo function: {return_list}')
        return return_list

    def get_version(self) -> list:
        """ Gets version info and returns it as a list

        Returns:
            list: Version info
                  0: Device Model, 1: Firmware Version
        """
        return_list = ['EDS-408A-MM-SC', 'V3.8']
        self.vprint(f'get_version function: {return_list}')
        return return_list

    def get_ifaces(self) -> list:
        """ Gets status of interfaces, and returns it as a list.
        
        Returns:
            list: Status of all interfaces
        """
        return_list = ['Down', 'Down', 'Down', 'Down', 'Down', 'Down', 'Down', 'Down']
        self.vprint(f'get_ifaces function: {return_list}')
        return return_list

    def get_portconfig(self) -> list:
        """ Gets the relay warning settings of the interfaces and returns it as a list.

        Returns:
            list: Relay warning status of all interfaces
        """
        return_list = ['Off', 'Ignore', 'Ignore', 'Off', 'Ignore', 'Off', 'Off', 'Ignore']
        self.vprint(f'get_portconfig function: {return_list}')
        return return_list

    def get_ip(self) -> list:
        """ Gets the current ip of the mgmt interface and returns it as a list.

        Returns:
            list: mgmt ip info
                  0: IPv4 VLAN id, 1: IP mode,
                  2: IPv4 address, 3: IPv4 Subnet,
                  4: IPv4 gateway, 5: IPv4 DNS,
                  6: IPv6 unicast prefix,
                  7: IPv6 unicast address,
                  8: IPv6 link local address
        """
        return_list = ['1', 'Static', '192.168.127.253', '255.255.255.0', '0.0.0.0', '', '', '::', 'fe80::290:e8ff:fe73:4655']
        self.vprint(f'get_ip function: {return_list}')
        return return_list

    def login_change(self) -> None:
        """ Change login mode to menu
        """
        self.vprint('login_change function: login mode to menu')

    def conf_iface(self, alarm:list) -> None:
        """ Configures alarm for interfaces in list. value == 1 is alarm on

        Args:
            alarm (list): interfaces with alarm on or off
        """
        # self.ser.write(b'configure\n')
        # self.ser.read_until(self.cprompt)
        # for iface in range(len(alarm)):
        #     self.ser.write(b'interface ethernet 1/'+ str(iface+1).encode('latin-1') + b'\n')
        #     self.ser.read_until(self.iprompt)
        #     if alarm[iface] == 1:
        #         self.vprint(f'conf_iface function: setting alarmstatus ON: {iface+1}')
        #         self.ser.write(b'relay-warning event link-off\n')
        #         self.ser.read_until(self.iprompt)
        #         self.ser.write(b'exit\n')
        #         self.ser.read_until(self.cprompt)
        #     else:
        #         self.vprint(f'conf_iface function: setting alarmstatus OFF: {iface+1}')
        #         self.ser.write(b'no relay-warning event link\n')
        #         self.ser.read_until(self.iprompt)
        #         self.ser.write(b'exit\n')
        #         self.ser.read_until(self.cprompt)
        # self.ser.write(b'exit\n')
        # self.ser.read_until(self.prompt)
        self.vprint(alarm)


    def conf_ip(self, ip:str) -> int:
        """ Changes the ip-address of the switch to (ip)

        Args:
            ip (str): IP Address to set
        Returns:
            status (int): -1 Success
                           0 Failed
                           1 Malformed IP
        """
        try:
            ip_address(ip)
        except: 
            return 1
        # self.ser.write(b'configure\n')
        # self.ser.read_until(self.cprompt)
        # self.ser.write(b'interface mgmt\n')
        # self.ser.read_until(self.vprompt)
        # self.ser.write(b'ip address static ' +
        #         ip.encode('latin-1') + b' 255.255.255.0\n')
        # self.ser.write(b'exit\n')
        # self.ser.write(b'exit\n')
        # self.ser.read_until(self.prompt)
        if self.get_ip()[2] != ip:
            self.vprint(f'IP address set to: {ip}')
            return 0
        self.vprint('IP address setting: Failure')
        return -1

    def conf_hostname(self, hostname:str) -> None:
        """ Changes the hostname of the switch

        Args:
            hostname (str): Hostname to switch to
        """
        # self.ser.write(b'configure\n')
        # self.ser.read_until(self.cprompt)
        # self.ser.write(b'hostname ' + hostname.encode('latin-1') + b'\n')
        # self.ser.read_until(self.cprompt)
        # self.ser.write(b'exit\n')
        # self.ser.read_until(self.prompt)
        self.vprint(f'Hostname set to: {hostname}')

    def conf_location(self, location:str) -> None:
        """ Changes the location parameter of the switch

        Args:
            location (str): location string to switch to
        """
        # self.ser.write(b'configure\n')
        # self.ser.read_until(self.cprompt)
        # self.ser.write(b'snmp-server location ' + location.encode('latin-1') + b'\n')
        # self.ser.read_until(self.cprompt)
        # self.ser.write(b'exit\n')
        # self.ser.read_until(self.prompt)
        self.vprint(f'Location set to: {location}')

    def factory_conf(self) -> None:
        """ Reset device to factory defaults
        """
        # self.ser.write(b'reload factory-default\n')
        # self.ser.read_until('Proceed with reload to factory default? [Y/n]')
        # self.ser.write(b'Y')
        self.vprint('Factory defaults set')
        pass

    def save_run2startup(self) -> bool:
        """ Saves the configuration from running to startup
        
        Returns:
            status (int): True = Success
                          False = Failure
        """
        # self.ser.write(b'save\n')
        # rval = self.ser.read_until(self.prompt)
        rval = b'Success'
        if br'Success' in rval:
            self.vprint('Saving running config to startup: Success')
            return True
        else:
            self.vprint('Saving running config to startup: Failure')
            return False

    def save_config(self) -> str:
        """ Gets the startup config and returns it as a decoded string

        Returns:
            config (str)
        """
        # self.ser.write(b'show startup-config\n')
        # config = self.ser.readlines()[3:-1]
        # config_dec = []
        # for items in config:
        #     config_dec.append(items.decode('latin-1'))
        # configstring = ''.join(config_dec)
        configstring = 'test test test'
        return configstring #[3:-1]

    def compare_config(self) -> int:
        """ Compares the running and startup config and returns status

        Returns:
            status (int): -1 = Match
                           0 = Mismatch
        """
        # self.ser.write(b'show startup-config\n')
        # startup = self.ser.readlines()[3:-1]
        # self.ser.write(b'show running-config\n')
        # running = self.ser.readlines()[3:-1]
        # self.vprint(f'Config status: {running}')
        # if startup == running:
        #     return -1
        self.vprint('compare_config function')
        return 0

    def get_eventlog(self) -> str:
        """ Returns the eventlog as a list

        Returns:
            eventlog (list)
        """
        # self.vprint('Getting event log')
        # self.ser.write(b'show logging event-log\n')
        # eventlog = self.ser.readlines()[1:-1]
        # eventlog_dec = []
        # for items in eventlog:
        #     eventlog_dec.append(items.decode('latin-1'))
        # eventstring = ''.join(eventlog_dec).rstrip()
        self.vprint('get_eventlog function: ')
        eventstring = ' test eventlog test'
        self.vprint(eventstring)
        return eventstring

    def clear_eventlog(self) -> None:
        """ Clears the eventlog
        """
        # self.ser.write(b'clear logging event-log\n')
        # self.ser.read_until(self.prompt)
        self.vprint('clear_eventlog function:')

    def copy_firmware(self, file:str) -> bool:
        """ Send firmware file to device
        
        Args:
            file str: filelocation with full path
        Returns:
            status (bool): True for success
                           False for failure
        """
        _ = file
        def progress(tp, sc, ec):
            self.total_packets = tp
            self.success_count = sc
            self.error_count = ec
            self.vprint(f'Total Packets: {self.total_packets}, Success Count: {self.success_count}, Error Count: {self.error_count}')

        self.vprint('copy_firmware function:')
        sleep(20)
        return True

if __name__ == "__main__":
        moxa_switch = Connection(verbose=True)
        logincheck = moxa_switch.check_login()
        if logincheck == 0:
            moxa_switch.menu_login()
        elif logincheck == 1:
            moxa_switch.cli_login()
            # print(moxa_switch.get_sysinfo())
            # print(moxa_switch.get_version())
            # print(moxa_switch.get_ifaces())
            print(moxa_switch.get_portconfig())
            alarms = [1,0,0,1,0,1,1,0] 
            moxa_switch.conf_iface(alarms)
            # print(moxa_switch.get_ip())
            # print(moxa_switch.get_eventlog())
            # moxa_switch.factory_conf()
            # print(moxa_switch.conf_ip('192.168.127.252'))
            input()
