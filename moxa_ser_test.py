#!/usr/bin/python3
"""Library to test GUI without connection to switch."""
from ipaddress import ip_address
from time import sleep


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
        xonxoff: int = 1,
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
        self.total_packets = 0
        self.success_count = 0
        self.error_count = 0

    def vprint(self, text) -> None:
        """Print only when verbose is true."""
        if self.verbose is True:
            print(f"Moxalib: {text}")

    def reset_conn(self) -> None:
        """Reset Connection."""
        pass

    def check_login(self):
        """
        Check if login mode is menu or cli.

        Returns:
                (0 is menu, 1 is cli, -1 when nothing matched)
        """
        return_val = 1
        self.vprint(f"check_login function: {return_val}")
        return return_val

    def menu_login(self, user: str = "admin", password: str = "") -> None:
        """
        Login with menu, and change to cli login.

        Args:
            user (str): username, default 'admin'
            password (str): password, default ''
        """
        self.vprint("Writing Account name: {}".format(user))
        self.vprint("Writing Password: {}".format(password))

    def cli_login(self, user: str = "admin", password: str = "") -> None:
        """
        Login with cli login.

        Args:
            user (str): username, default 'admin'
            password (str): password, default ''
        """
        self.vprint("Writing Account name: {}".format(user))
        self.vprint("Writing Password: {}".format(password))

    def keepalive(self) -> int:
        """
        Keep user logged in.

        Returns:
            int: -1: OK
                  0: Error
        """
        self.vprint("keepalive function: -1")
        return -1

    def get_sysinfo(self) -> list:
        """
        Get system info and returns it as a list.

        Returns:
            list: System parameters
                  0: System Name, 1: Switch Location,
                  2: Switch Description, 3: Maintainer Info,
                  4: MAC Address, 5: Switch Uptime
        """
        return_list = [
            "Managed Redundant Switch 06113",
            "Switch Location",
            "EDS-408A-MM-SC",
            "",
            "00:90:E8:73:46:55",
            "0d0h40m48s",
        ]
        self.vprint(f"get_sysinfo function: {return_list}")
        return return_list

    def get_version(self) -> list:
        """
        Get version info and returns it as a list.

        Returns:
            list: Version info
                  0: Device Model, 1: Firmware Version
        """
        return_list = ["EDS-408A-MM-SC", "V3.8"]
        self.vprint(f"get_version function: {return_list}")
        return return_list

    def get_ifaces(self) -> list:
        """
        Get status of interfaces, and returns it as a list.

        Returns:
            list: Status of all interfaces
        """
        return_list = ["Up", "Down", "Down", "Up", "Down", "Down", "Down", "Down"]
        self.vprint(f"get_ifaces function: {return_list}")
        return return_list

    def get_portconfig(self) -> list:
        """
        Get the relay warning settings of the interfaces and returns it as a list.

        Returns:
            list: Relay warning status of all interfaces
        """
        return_list = [
            "Off",
            "Ignore",
            "Ignore",
            "Off",
            "Ignore",
            "Off",
            "Off",
            "Ignore",
        ]
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
        return_list = [
            "1",
            "Static",
            "192.168.127.253",
            "255.255.255.0",
            "0.0.0.0",
            "",
            "",
            "::",
            "fe80::290:e8ff:fe73:4655",
        ]
        self.vprint(f"get_ip function: {return_list}")
        return return_list

    def login_change(self) -> None:
        """Change login mode to menu."""
        self.vprint("login_change function: login mode to menu")

    def conf_iface(self, alarm: list) -> None:
        """
        Configure alarm for interfaces in list. value == 1 is alarm on.

        Args:
            alarm (list): interfaces with alarm on or off
        """
        self.vprint(alarm)

    def conf_ip(self, ip: str) -> int:
        """
        Change the ip-address of the switch to (ip).

        Args:
            ip (str): IP Address to set
        Returns:
            status (int): -1 Success
                           0 Failed
                           1 Malformed IP
        """
        try:
            ip_address(ip)
        except ValueError:
            return 1
        if self.get_ip()[2] != ip:
            self.vprint(f"IP address set to: {ip}")
            return 0
        self.vprint("IP address setting: Failure")
        return -1

    def conf_hostname(self, hostname: str) -> None:
        """
        Change the hostname of the switch.

        Args:
            hostname (str): Hostname to switch to
        """
        self.vprint(f"Hostname set to: {hostname}")

    def conf_location(self, location: str) -> None:
        """
        Change the location parameter of the switch.

        Args:
            location (str): location string to switch to
        """
        self.vprint(f"Location set to: {location}")

    def factory_conf(self) -> None:
        """Reset device to factory defaults."""
        self.vprint("Factory defaults set")
        pass

    def save_run2startup(self) -> bool:
        """
        Save the configuration from running to startup.

        Returns:
            status (int): True = Success
                          False = Failure
        """
        rval = b"Success"
        if rb"Success" in rval:
            self.vprint("Saving running config to startup: Success")
            return True
        else:
            self.vprint("Saving running config to startup: Failure")
            return False

    def save_config(self) -> str:
        """
        Get the startup config and return it as a decoded string.

        Returns:
            config (str)
        """
        configstring = "test test test"
        return configstring  # [3:-1]

    def compare_config(self) -> int:
        """
        Compare the running and startup config and return status.

        Returns:
            status (int): -1 = Match
                           0 = Mismatch
        """
        self.vprint("compare_config function")
        return 0

    def get_eventlog(self) -> str:
        """
        Return the eventlog as a list.

        Returns:
            eventlog (list)
        """
        self.vprint("get_eventlog function: ")
        eventstring = " test eventlog test"
        self.vprint(eventstring)
        return eventstring

    def clear_eventlog(self) -> None:
        """Clear the eventlog."""
        self.vprint("clear_eventlog function:")

    def copy_firmware(self, file: str) -> bool:
        """
        Send firmware file to device.

        Args:
            file str: filelocation with full path
        Returns:
            status (bool): True for success
                           False for failure
        """
        _ = file

        self.vprint("copy_firmware function:")
        sleep(20)
        return True


if __name__ == "__main__":
    pass
