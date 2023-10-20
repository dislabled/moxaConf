#!/usr/bin/python3
"""
Moxalib.

This module uses a serial connection to communicate with moxa eds routers
for common configuring.

Todo:
    # set time : configure -> clock set hh:mm:ss month day year

"""
import re
from time import sleep
from ipaddress import ip_address
from serial import Serial  # type: ignore
from xmodem import XMODEM, NAK  # type: ignore


def expect(buffer: list, wtf: list) -> int:
    """
    Find a string in read value.

    Args:
        buffer (list): the text to be searched
        wtf (str): what to find

    Returns:
        int: stringindex for match,
             -1 if nothing found,
             -2 if empty buffer
    """
    findval = buffer[-1]
    for index, value in enumerate(wtf):
        if findval.find(value) != -1:
            return index
    return -1


class Connection:
    """Function on a serial object for moxa EDS routers."""

    def __init__(
        self,
        device: str = "/dev/ttyUSB0",
        baud: int = 115200,
        timeout: int = 1,
        prompt: bytes = b"EDS-408A-MM-SC",
        xonxoff: bool = True,
        verbose: bool = False,
    ) -> None:
        """Initialize the class."""
        self.device = device
        self.baud = baud
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.verbose = verbose
        self.p_end = b"#"
        self.prompt = prompt + self.p_end
        self.cprompt = prompt + b"(config)" + self.p_end
        self.iprompt = prompt + b"(config-if)" + self.p_end
        self.vprompt = prompt + b"(config-vlan)" + self.p_end
        self.serial = Serial(
            port=self.device,
            baudrate=self.baud,
            timeout=self.timeout,
            xonxoff=self.xonxoff,
        )
        self.total_packets = 0
        self.success_count = 0
        self.error_count = 0

    def vprint(self, text) -> None:
        """Print only when verbose is true."""
        if self.verbose is True:
            print(f"Moxalib: {text}")

    def reset_conn(self) -> list:
        """Reset Connection."""
        input_buffer = self.serial.readlines()
        while not input_buffer:
            self.serial.setDTR(0)  # type: ignore
            sleep(0.5)
            self.serial.setDTR(1)  # type: ignore
            input_buffer = self.serial.readlines()
        return input_buffer

    def check_login(self):
        """
        Check if login mode is menu or cli.

        Returns:
                (0 is menu, 1 is cli, -1 when nothing matched)
        """
        buffer = self.reset_conn()
        returnval = expect(buffer, [b"vt52) : 1", b"login as:"])
        self.vprint(f"check_login function: {returnval}")
        return returnval

    def menu_login(self, user: str = "admin", password: str = "") -> None:
        """
        Login with menu, and change to cli login.

        Args:
            user (str): username, default 'admin'
            password (str): password, default ''
        """
        self.vprint("Entering Ansi terminal...")
        # Press enter to use ansi terminal
        self.serial.write(b"\r")
        account_mode = expect(self.serial.readlines(), [rb"[admin]"])
        if account_mode == 0:
            self.vprint("Selecting Account name: {}".format(user))
            # Select username
            self.serial.write(b"\x1b[B")
        else:
            self.vprint(f"menu_login function: Writing Account name: {user}")
            sleep(2)
            # Enter Username
            self.serial.write(user.encode("latin-1") + "\n".encode("latin-1"))
        self.vprint(f"menu_login function: Writing Password: {password}")
        # Enter password
        self.serial.write(password.encode("latin-1") + "\n".encode("latin-1"))
        sleep(0.2)
        weak_password_prompt = expect(self.serial.readlines(), [rb"Enter to select"])
        if weak_password_prompt == -1:
            # Clear weak password popup (on newer firmware)
            self.serial.write(b"\n")
            sleep(0.2)
        self.vprint('menu_login function: Entering "Basic" menu...')
        # Enter menu - Basic
        self.serial.write(b"1\n")
        sleep(0.2)
        self.vprint('menu_login function: Entering "Login mode" menu...')
        # Enter menu login mode
        self.serial.write(b"l\n")
        sleep(0.2)
        self.vprint('menu_login function: Entering "yes" to switch mode...')
        # Enter yes to switch to CLI
        self.serial.write(b"Y\n")
        self.vprint("menu_login function: Restarting Connection")

    def cli_login(self, user: str = "admin", password: str = "") -> None:
        """
        Login with cli login.

        Args:
            user (str): username, default 'admin'
            password (str): password, default ''
        """
        self.vprint(f"cli_login function: Writing Account name: {user}")
        # Enter username
        self.serial.write(user.encode("latin-1") + b"\n")
        self.vprint(f"cli_login function: Writing Password: {password}")
        # Enter password
        self.serial.write(password.encode("latin-1") + b"\n")
        # Clear potential weak password popup (on newer firmware)
        self.serial.write("\n".encode("latin-1"))
        # Change terminal length to unlimited to dismiss pager
        self.serial.write(b"terminal length 0\n")
        # Clear buffer
        self.serial.readlines()[-1].decode("latin-1")

    def keepalive(self) -> bool:
        """
        Keep the user logged in.

        Returns:
            bool: True: OK
                  False: Error
        """
        self.serial.write(b"\n")
        if self.serial.readlines()[-1].rstrip() != self.prompt:
            return False
        self.vprint("keepalive function")
        return True

    def get_sysinfo(self) -> list:
        """
        Get system info and returns it as a list.

        Returns:
            list: System parameters
                  0: System Name, 1: Switch Location,
                  2: Switch Description, 3: Maintainer Info,
                  4: MAC Address, 5: Switch Uptime
        """
        self.serial.write(b"show system\n")
        sysinfo = self.serial.read_until(self.prompt).decode("latin-1")
        return_list = re.findall("(?<=: )(.*)\\r", sysinfo.strip())
        self.vprint(f"get_sysinfo function: {return_list}")
        return return_list

    def get_version(self) -> list:
        """
        Get version info and returns it as a list.

        Returns:
            list: Version info
                  0: Device Model, 1: Firmware Version
        """
        self.serial.flush()
        self.serial.write(b"show version\n")
        version = self.serial.read_until(self.prompt).decode("latin-1")
        return_list = re.findall("(?<=: )(.*)\\r", version.strip())
        self.vprint(f"get_version function: {return_list}")
        return return_list

    def get_ifaces(self) -> list:
        """
        Get status of interfaces, and returns it as a list.

        Returns:
            list: Status of all interfaces
        """
        self.serial.flush()
        self.serial.write(b"show interfaces ethernet\n")
        return_list = re.findall(
            "(?<=(?:1/.{3}))\\w+", self.serial.read_until(self.prompt).decode("latin-1")
        )
        self.vprint(f"get_ifaces function: {return_list}")
        return return_list

    def get_portconfig(self) -> list:
        """
        Get the relay warning settings of the interfaces and returns it as a list.

        Returns:
            list: Relay warning status of all interfaces
        """
        self.serial.write(b"show relay-warning config\n")
        return_list = re.findall(
            "(?<=(?:1/.).{10})\\w+",
            self.serial.read_until(self.prompt).decode("latin-1"),
        )
        self.vprint(f"get_portconfig function: {return_list}")
        return return_list

    def get_ip(self) -> list:
        """
        Get the current ip of the mgmt interface and returns it as a list.

        Returns:
            list: mgmt ip info
                  0: IPv4 VLAN id, 1: IP mode,
                  2: IPv4 address, 3: IPv4 Subnet,
                  4: IPv4 gateway, 5: IPv4 DNS,
                  6: IPv6 unicast prefix,
                  7: IPv6 unicast address,
                  8: IPv6 link local address
        """
        self.serial.write(b"show interfaces mgmt\n")
        ipinfo = self.serial.read_until(self.prompt).decode("latin-1")
        return_list = re.findall("(?<=: )(.*)\\r", ipinfo.strip())
        self.vprint(f"get_ip function: {return_list}")
        return return_list

    def login_change(self) -> None:
        """Change login mode to menu."""
        self.vprint("login_change function: Changing login mode to menu")
        self.serial.write(b"login mode menu\n")

    def conf_iface(self, alarm: list) -> None:
        """
        Configure alarm for interfaces in list. value == 1 is alarm on.

        Args:
            alarm (list): interfaces with alarm on or off
        """
        self.serial.write(b"configure\n")
        self.serial.read_until(self.cprompt)
        for count, iface in enumerate(alarm):
            self.serial.write(
                b"interface ethernet 1/" + str(count + 1).encode("latin-1") + b"\n"
            )
            self.serial.read_until(self.iprompt)
            if iface == 1:
                self.vprint(f"conf_iface function: set alarm on iface{count + 1} ON")
                self.serial.write(b"relay-warning event link-off\n")
                self.serial.read_until(self.iprompt)
                self.serial.write(b"exit\n")
                self.serial.read_until(self.cprompt)
            else:
                self.vprint(f"conf_iface function: set alarm on iface{count + 1} OFF")
                self.serial.write(b"no relay-warning event link\n")
                self.serial.read_until(self.iprompt)
                self.serial.write(b"exit\n")
                self.serial.read_until(self.cprompt)
        self.serial.write(b"exit\n")
        self.serial.read_until(self.prompt)

    def conf_ip(self, ip_add: str) -> int:
        """
        Change the ip-address of the switch to (ip).

        Args:
            ip_add (str): IP Address to set
        Returns:
            status (int): -1 Success
                           0 Failed
                           1 Malformed IP
        """
        try:
            ip_address(ip_add)
        except ValueError:
            return 1
        self.serial.write(b"configure\n")
        self.serial.read_until(self.cprompt)
        self.serial.write(b"interface mgmt\n")
        self.serial.read_until(self.vprompt)
        self.serial.write(
            b"ip address static " + ip_add.encode("latin-1") + b" 255.255.255.0\n"
        )
        self.serial.write(b"exit\n")
        self.serial.write(b"exit\n")
        self.serial.read_until(self.prompt)
        if self.get_ip()[2] != ip_add.encode("latin-1"):
            self.vprint(f"conf_ip function: set: {ip_add}")
            return 0
        self.vprint("conf_ip function: Failure")
        return -1

    def conf_hostname(self, hostname: str) -> None:
        """
        Change the hostname of the switch.

        Args:
            hostname (str): Hostname to switch to
        """
        self.serial.write(b"configure\n")
        self.serial.read_until(self.cprompt)
        self.serial.write(b"hostname " + hostname.encode("latin-1") + b"\n")
        self.serial.read_until(self.cprompt)
        self.serial.write(b"exit\n")
        self.serial.read_until(self.prompt)
        self.vprint(f"conf_hostname function: set {hostname}")

    def conf_location(self, location: str) -> None:
        """Change the location parameter of the switch.

        Args:
            location (str): location string to switch to
        """
        self.serial.write(b"configure\n")
        self.serial.read_until(self.cprompt)
        self.serial.write(b"snmp-server location " + location.encode("latin-1") + b"\n")
        self.serial.read_until(self.cprompt)
        self.serial.write(b"exit\n")
        self.serial.read_until(self.prompt)
        self.vprint(f"conf_location function: set to: {location}")

    def factory_conf(self) -> None:
        """Reset device to factory defaults."""
        self.serial.write(b"reload factory-default\n")
        self.serial.read_until(b"Proceed with reload to factory default? [Y/n]")
        self.serial.write(b"Y")
        self.vprint("factory_conf function: Factory defaults set")

    def save_run2startup(self) -> bool:
        """
        Save the configuration from running to startup.

        Returns:
            status (int): True = Success
                          False = Failure
        """
        self.serial.write(b"save\n")
        rval = self.serial.read_until(self.prompt)
        if rb"Success" in rval:
            self.vprint("Saving running config to startup: Success")
            return True
        self.vprint("Saving running config to startup: Failure")
        return False

    def save_config(self) -> str:
        """Get the startup config and returns it as a decoded string.

        Returns:
            config (str)
        """
        self.serial.write(b"show startup-config\n")
        config = self.serial.readlines()[3:-1]
        config_dec = []
        for items in config:
            config_dec.append(items.decode("latin-1"))
        configstring = "".join(config_dec)
        return configstring  # [3:-1]

    def compare_config(self) -> int:
        """Compare the running and startup config and returns status.

        Returns:
            status (int): -1 = Match
                           0 = Mismatch
        """
        self.serial.write(b"show startup-config\n")
        startup = self.serial.readlines()[3:-1]
        self.serial.write(b"show running-config\n")
        running = self.serial.readlines()[3:-1]
        self.vprint(f"compare_config function: {running}")
        if startup == running:
            return -1
        return 0

    def get_eventlog(self) -> str:
        """
        Return the eventlog as a list.

        Returns:
            eventlog (list)
        """
        self.vprint("get_eventlog function: ")
        self.serial.write(b"show logging event-log\n")
        eventlog = self.serial.readlines()[1:-1]
        eventlog_dec = []
        for items in eventlog:
            eventlog_dec.append(items.decode("latin-1"))
        eventstring = "".join(eventlog_dec).rstrip()
        self.vprint(eventstring)
        return eventstring

    def clear_eventlog(self) -> None:
        """Clear the eventlog."""
        self.serial.write(b"clear logging event-log\n")
        self.serial.read_until(self.prompt)

    def copy_firmware(self, file: str) -> bool:
        """
        Send firmware file to device.

        Args:
            file str: filelocation with full path
        Returns:
            status (bool): True for success
                           False for failure
        """

        def getc(size, timeout=1) -> bytes | None:
            """Retrieve the bytes from the stream."""
            _ = timeout
            return self.serial.read(size) or None

        def putc(data, timeout=1) -> int | None:
            """Receive the bytes from the stream."""
            _ = timeout
            return self.serial.write(data)

        def progress(total_packets, success_count, error_count):
            """Get the transmit data."""
            self.total_packets = total_packets
            self.success_count = success_count
            self.error_count = error_count
            self.vprint(
                f"Total Packets: {self.total_packets},"
                f" Success Count: {self.success_count},"
                f" Error Count: {self.error_count}"
            )

        self.serial.write(b"copy xmodem device-firmware\n")
        self.serial.write(NAK)  # send ^U (NAK)
        self.serial.readlines()  # empty buffer, ready to send
        modem = XMODEM(getc, putc)
        with open(file, "rb") as stream:
            return modem.send(stream, retry=8, callback=progress)


if __name__ == "__main__":
    moxa_switch = Connection(verbose=True)
    logincheck = moxa_switch.check_login()
    if logincheck == 0:
        moxa_switch.menu_login()
    elif logincheck == 1:
        moxa_switch.cli_login()
        moxa_switch.get_sysinfo()
        moxa_switch.get_version()
        moxa_switch.get_ifaces()
        moxa_switch.get_portconfig()
        moxa_switch.get_ip()
        input("press any key to quit")
    else:
        print("Cannot log in: ", +logincheck)
