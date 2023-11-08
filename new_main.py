#!/usr/bin/env python3
# -*- coding=utf-8 -*-
"""Main GUI for moxa configurator."""
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import filedialog as fd

from moxa_ser_test import Connection
from moxa_csv_lib import ConfigFile


class MainApp(tk.Tk):
    """Root window for moxa configurator."""

    def __init__(self, title: str = "Moxa Configurator", size: tuple = (800, 300)):
        """Initialize the class."""
        super().__init__()
        # Main setup.
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.minsize(size[0], size[1])
        self.bind("<Escape>", lambda _: self.destroy())

        # Create some "globals".
        self.shared_vals: dict = {
            "toggle_conf": tk.IntVar(value=0),
            "toggle_mainred": tk.IntVar(value=0),
            "logged_in": tk.BooleanVar(value=False),
            "active_side_frame": tk.IntVar(value=0),
            "active_main_frame": tk.IntVar(value=0),
        }
        # Monitor the globals.
        self.shared_vals["active_side_frame"].trace("w", self.menu_frame)
        self.shared_vals["active_main_frame"].trace("w", self.main_frame)

        # Open the frames.
        self.menu_frame(self.shared_vals)
        self.main_frame()

        # Create the main frame.
        self.mainloop()

    def menu_frame(self, *args):
        """Return the menu frame."""
        _ = args  # Hush some editor warnings
        menu_frame = ttk.Frame(self)
        menu_frame.place(relx=0, rely=0, width=250, relheight=1)
        if self.shared_vals["active_side_frame"].get() == 0:
            MainMenu(menu_frame, self.shared_vals)
        else:
            AutoConfMenu(menu_frame, self.shared_vals)

    def main_frame(self, *args):
        """Return the main frame."""
        _ = args  # Hush some editor warnings
        main_frame = ttk.Frame(self)
        main_frame.place(relx=0.25, rely=0, relwidth=0.75, relheight=1)
        if self.shared_vals["active_main_frame"].get() == 0:
            pass
        elif self.shared_vals["active_main_frame"].get() == 1 and self.shared_vals["logged_in"].get() is True:
            SwitchInfo(main_frame)
            Ports(main_frame)
        elif self.shared_vals["active_main_frame"].get() == 2:
            AutoConf(main_frame, self.shared_vals)


class MainMenu(ttk.Frame):
    """Main menu buttons."""

    def __init__(self, parent, shared_vals):
        """Initialize the class."""
        super().__init__(parent)
        self.logged_in = shared_vals["logged_in"]
        self.active_main_frame = shared_vals["active_main_frame"]
        self.active_side_frame = shared_vals["active_side_frame"]
        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        """Create the widgets."""
        self.menuframe = ttk.LabelFrame(self, text="Menu")
        self.button0 = tk.Button(self.menuframe, text="Connect", width=13, command=self.connect)
        self.button1 = tk.Button(self.menuframe, text="Download config", width=13, command=self.download_config)
        self.button2 = tk.Button(
            self.menuframe,
            text="Transfer firmware",
            width=13,
        )
        self.button3 = tk.Button(self.menuframe, text="Auto configure", width=13, command=self.autoconfig)
        self.button4 = tk.Button(self.menuframe, text="Factory reset", width=13, command=self.factory_reset)
        self.button5 = tk.Button(
            self.menuframe,
            text="Alarm log",
            width=13,
        )
        self.button6 = tk.Button(self.menuframe, text="Copy ram2rom", width=13, command=self.apply)

    def create_layout(self):
        """Create the layout."""
        self.menuframe.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.button0.grid(row=0, column=0, padx=2, pady=2)
        self.button1.grid(row=1, column=0, padx=2, pady=2)
        self.button2.grid(row=2, column=0, padx=2, pady=2)
        self.button3.grid(row=3, column=0, padx=2, pady=2)
        self.button4.grid(row=4, column=0, padx=2, pady=2)
        self.button5.grid(row=5, column=0, padx=2, pady=2)
        self.button6.grid(row=6, column=0, padx=2, pady=2)
        self.pack()

    def factory_reset(self):
        """Reset switch to factory settings."""
        if mb.askokcancel(title="Warning", message="Do you wish to proceed?"):
            self.config(cursor="watch")
            moxa_switch.factory_conf()
            sys.exit(0)

    def download_config(self):
        """Download the switch running config."""
        initial_file = moxa_switch.get_sysinfo()[0]
        filename = fd.asksaveasfilename(
            defaultextension=".ini",
            initialdir="./site/configs/",
            initialfile=initial_file,
        )
        if filename != ():
            contents = moxa_switch.save_config()
            with open(filename, "w") as config:
                config.write(contents)

    def apply(self):
        """Save the running config to startup config."""
        if moxa_switch.save_run2startup():
            mb.showinfo(message="Success")
        else:
            mb.showerror(title="Error", message="Something went wrong")

    def connect(self):
        """Connect to switch."""
        self.config(cursor="watch")
        login_mode = moxa_switch.check_login()
        if login_mode == 0:
            moxa_switch.menu_login()
        else:
            moxa_switch.cli_login()
        self.active_main_frame.set(1)
        self.logged_in.set(True)
        self.config(cursor="")

    def autoconfig(self):
        """Change frames."""
        self.active_side_frame.set(1)
        self.active_main_frame.set(2)


class SwitchInfo(ttk.Frame):
    """Switch info frame for moxa configurator."""

    def __init__(self, parent):
        """Initialize the class."""
        super().__init__(parent)
        self.create_widgets()
        self.create_layout()
        self.refresh()

    def create_widgets(self):
        """Create the widgets."""
        self.name_label = tk.Label(self, text="Name: ")
        self.switch_name = tk.Entry(self, width=24)
        self.upd_btn1 = tk.Button(self, text="Update", command=self.upd_name)
        self.loc_label = tk.Label(self, text="Location: ")
        self.swloc = tk.Entry(self, width=24)
        self.upd_btn2 = tk.Button(self, text="Update", command=self.upd_loc)
        self.desc_label = tk.Label(self, text="Description: ")
        self.swdesc = tk.Text(self, height=1, width=24)
        self.mac_label = tk.Label(self, text="MAC addr: ")
        self.swmac = tk.Text(self, height=1, width=17)
        self.swupt_label = tk.Label(self, text="Uptime: ")
        self.swupt = tk.Text(self, height=1, width=12)
        self.swver_label = tk.Label(self, text="Model Version: ")
        self.swver = tk.Text(self, height=1, width=24)
        self.swswv_label = tk.Label(self, text="Software ver: ")
        self.swswv = tk.Text(self, height=1, width=24)
        self.swip_label = tk.Label(self, text="IP addr: ")
        self.swip = tk.Entry(self, width=24)
        self.upd_btn3 = tk.Button(self, text="Update", command=self.upd_ip)

    def create_layout(self):
        """Create the layout."""
        self.name_label.grid(row=0, column=0, sticky="w", padx=5, pady=1)
        self.switch_name.grid(row=0, column=1, sticky="w", padx=5, pady=1)
        self.upd_btn1.grid(row=0, column=2)
        self.loc_label.grid(row=1, column=0, sticky="w", padx=5, pady=1)
        self.swloc.grid(row=1, column=1, sticky="w", padx=5, pady=1)
        self.upd_btn2.grid(row=1, column=2)
        self.desc_label.grid(row=2, column=0, sticky="w", padx=5, pady=1)
        self.swdesc.grid(row=2, column=1, sticky="w", padx=5, pady=1)
        self.mac_label.grid(row=3, column=0, sticky="w", padx=5, pady=1)
        self.swmac.grid(row=3, column=1, sticky="w", padx=5, pady=1)
        self.swupt_label.grid(row=4, column=0, sticky="w", padx=5, pady=1)
        self.swupt.grid(row=4, column=1, sticky="w", padx=5, pady=1)
        self.swver_label.grid(row=5, column=0, sticky="w", padx=5, pady=1)
        self.swver.grid(row=5, column=1, sticky="w", padx=5, pady=1)
        self.swswv_label.grid(row=6, column=0, sticky="w", padx=5, pady=1)
        self.swswv.grid(row=6, column=1, sticky="w", padx=5, pady=1)
        self.swip_label.grid(row=7, column=0, sticky="w", padx=5, pady=1)
        self.swip.grid(row=7, column=1, sticky="w", padx=5, pady=1)
        self.upd_btn3.grid(row=7, column=2)
        self.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    def upd_name(self):
        """Write the new hostname."""
        moxa_switch.conf_hostname(self.switch_name.get())

    def upd_loc(self):
        """Write the new location."""
        moxa_switch.conf_location(self.swloc.get())

    def upd_ip(self):
        """Write the new IP address."""
        moxa_switch.conf_ip(self.swip.get())

    def refresh(self) -> None:
        """Read and refresh values on screen."""
        # Read new values
        self.system = moxa_switch.get_sysinfo()
        self.version = moxa_switch.get_version()
        self.mgmt_ip = moxa_switch.get_ip()
        # Delete old values
        self.switch_name.delete(0, tk.END)
        self.swloc.delete(0, tk.END)
        self.swdesc.delete(1.0, tk.END)
        self.swmac.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.NORMAL)
        self.swmac.delete(1.0, tk.END)
        self.swupt.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.NORMAL)
        self.swupt.delete(1.0, tk.END)
        self.swver.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.NORMAL)
        self.swver.delete(1.0, tk.END)
        self.swswv.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.NORMAL)
        self.swswv.delete(1.0, tk.END)
        self.swip.delete(0, tk.END)
        # Insert new values
        self.switch_name.insert(tk.END, self.system[0])
        self.swloc.insert(tk.END, self.system[1])
        self.swdesc.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.DISABLED)
        self.swdesc.insert(tk.END, self.system[2])
        self.swmac.insert(tk.END, self.system[4])
        self.swmac.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.DISABLED)
        self.swupt.insert(tk.END, self.system[5])
        self.swupt.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.DISABLED)
        self.swver.insert(tk.END, self.version[0])
        self.swver.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.DISABLED)
        self.swswv.insert(tk.END, self.version[1])
        self.swswv.config(bg="#D9D9D9", relief=tk.FLAT, state=tk.DISABLED)
        self.swip.insert(tk.END, self.mgmt_ip[2])
        self.config(cursor="")


class Ports(ttk.Frame):
    """Port configuration frame."""

    def __init__(self, parent, ports: int = 8):
        """Initialize the class."""
        super().__init__(parent)
        self.alobjports: list = [tk.IntVar() for _ in range(ports)]
        self.create_widgets(ports)
        self.refresh()

    def create_widgets(self, ports):
        """Create widgets."""
        portheight = int(ports / 2) + 2

        self.portframe = ttk.LabelFrame(self, text="Ports")
        self.portframe.grid(row=0, column=0, columnspan=4, rowspan=8, sticky="nsew", padx=10, pady=10)
        column_gen = 3
        self.portbutton = {}
        for port in range(ports):
            self.portbutton[port] = tk.Checkbutton(
                self.portframe, text=str(port + 1), variable=self.alobjports[port], command=lambda: self.refresh()
            )
            self.portbutton[port].grid(row=portheight, column=column_gen, sticky="w", padx=5, pady=2)
            if column_gen == 1:
                column_gen = 3
                portheight -= 1
            else:
                column_gen = 1

        self.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def refresh(self):
        """Refresh port values."""
        self.config(cursor="watch")
        self.alintports = moxa_switch.get_portconfig()
        self.stintports = moxa_switch.get_ifaces()
        templist = []
        for port in self.alobjports:
            templist.append(port.get())
        moxa_switch.conf_iface(templist)
        self.portalarms()
        self.portcolor()
        self.config(cursor="")

    def portcolor(self) -> None:
        """Set background colors of connected ports."""
        for count, port in enumerate(self.stintports):
            if port == "Up":
                self.portbutton[count].config(bg="#000fff000")  # Green
            else:
                self.portbutton[count].config(bg="#D9D9D9")  # Same as background

    def portalarms(self) -> None:
        """Set status of alarms on ports."""
        for num, val in enumerate(self.alintports):
            if val == "Off":
                self.alobjports[num].set(True)


class AutoConfMenu(ttk.Frame):
    """Auto configuration Frame."""

    def __init__(self, parent, shared_vals) -> None:
        """Initialize the class."""
        super().__init__(parent)
        self.toggle_conf = shared_vals["toggle_conf"]
        self.toggle_mainred = shared_vals["toggle_mainred"]
        self.active_main_frame = shared_vals["active_main_frame"]
        self.active_side_frame = shared_vals["active_side_frame"]
        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        """Create the widgets."""
        self.menuframe = ttk.LabelFrame(self, text="Menu")
        self.button0 = tk.Button(self.menuframe, text="Return", width=13, command=self.window_control)
        self.button1 = tk.Button(self.menuframe, text="Show Reserve", width=13, command=self.button1_switch)
        self.button2 = tk.Button(self.menuframe, text="Show unconfigured", width=13, command=self.button2_switch)

    def create_layout(self):
        """Create the layout."""
        self.menuframe.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.button0.grid(row=0, column=0, padx=2, pady=2)
        self.button1.grid(row=1, column=0, padx=2, pady=2)
        self.button2.grid(row=2, column=0, padx=2, pady=2)
        self.pack(expand=True, fill="both")

    def button1_switch(self) -> None:
        """Toggle switch On/Off."""
        if self.toggle_mainred.get() == 0:
            self.button1.configure(text="Show Main")
            self.toggle_mainred.set(1)
        else:
            self.button1.configure(text="Show Reserve")
            self.toggle_mainred.set(0)

    def button2_switch(self) -> None:
        """Toggle switch On/Off."""
        if self.toggle_conf.get() == 0:
            self.button2.configure(text="Show All")
            self.toggle_conf.set(1)
        else:
            self.button2.configure(text="Show unconfigured")
            self.toggle_conf.set(0)

    def window_control(self) -> None:
        """Change frames."""
        self.active_side_frame.set(0)
        self.active_main_frame.set(0)


class AutoConf(ttk.Frame):
    """Devicewindow GUI for moxa configurator."""

    def __init__(self, parent, shared_vals) -> None:
        """Initialize the class."""
        super().__init__(parent)
        self.config_file = ConfigFile()
        self.file = "/home/stian/Projects/moxaConf/site/test.csv"
        self.toggle_conf = shared_vals["toggle_conf"]
        self.toggle_mainred = shared_vals["toggle_mainred"]
        self.toggle_conf.trace("w", self.refresh)
        self.toggle_mainred.trace("w", self.refresh)
        self.header_message = tk.StringVar()

        self.create_frames()
        self.header()
        self.treeview_widgets()
        self.create_layout()

    def create_frames(self) -> None:
        """Create the frames."""
        self.header_frame = tk.Frame(self)
        self.treeview_frame = tk.Frame(self)
        self.status_frame = tk.Frame(self)

    def create_layout(self) -> None:
        """Create the layout."""
        self.header_frame.pack(fill=tk.BOTH)
        self.treeview_frame.pack(fill=tk.BOTH, expand=True)
        self.status_frame.pack(fill=tk.BOTH)
        self.scrollbar.pack(fill=tk.BOTH, side="right")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.pack(fill=tk.BOTH, expand=True, padx=10)

    def header(self) -> None:
        """Create the header frame."""
        self.header_message = tk.StringVar()
        self.header_message.set("test")
        self.label = tk.Label(self.header_frame, text=self.header_message.get())
        self.label.pack(fill=tk.BOTH, expand=True)

    def treeview_widgets(self) -> None:
        """Create the treeview frame."""
        self.columns = ("cab", "ap", "sw_ip", "loc")
        self.tree = ttk.Treeview(self.treeview_frame, columns=self.columns, show="headings")
        self.tree.column("cab", width=130, anchor=tk.NW)
        self.tree.heading("cab", text="Cabinet")
        self.tree.column("ap", width=60, anchor=tk.NW)
        self.tree.heading("ap", text="AP")
        self.tree.column("sw_ip", width=140, anchor=tk.NW)
        self.tree.heading("sw_ip", text="Switch IP")
        self.tree.column("loc", width=350, anchor=tk.NW)
        self.tree.heading("loc", text="Location")
        self.tree.bind("<Double-1>", self.item_selected)
        self.tree.bind("<KeyRelease-Return>", self.item_selected)
        self.scrollbar = ttk.Scrollbar(self.treeview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.refresh()

    def item_selected(self, event) -> None:
        """Get selected value and write config to switch."""
        _ = event  # Hush some editor warnings
        config = self.tree.item(self.tree.focus())["values"]
        ports = [0, 0, 0, 0, 0, 0, 0, 0]
        for count, port in enumerate(moxa_switch.get_ifaces()):
            if port == "Up":
                ports[count] = 1
        if self.toggle_mainred.get() == 0:
            main_reserve = "M"
        else:
            main_reserve = "R"
        message = (
            f"Hostname: {config[0] + main_reserve}\n"
            f"Location: {config[3]}\n"
            f"IP Address: {config[2]}\n"
            f"Alarm on {ports}"
        )
        if mb.askokcancel(title="Continue?", message=message):
            moxa_switch.conf_hostname(config[0] + main_reserve)
            moxa_switch.conf_location(config[3])
            moxa_switch.conf_ip(config[2])
            moxa_switch.conf_iface(ports)
            moxa_switch.save_run2startup()
            self.config_file.write_config(
                self.file,
                config[0],
                config[1],
                moxa_switch.get_sysinfo()[4],
                True if self.toggle_mainred.get() == 0 else False,
            )
            self.refresh()

    def refresh(self, *args) -> None:
        """Refresh the values in the frame."""
        _ = args  # Hush some editor warnings
        if self.file == "":
            file = fd.askopenfilename(initialdir="./site/", filetypes=[("Comma Separated files", ".csv")])
            if file != "":
                self.file = file

        # Clear tree
        for entry in self.tree.get_children():
            self.tree.delete(entry)
        # Update values in tree
        for entry in self.read_config(self.file):
            self.tree.insert("", tk.END, values=list(entry))
        self.tree.selection_set(self.tree.get_children()[0])

        # Configure dynamic header
        if self.toggle_mainred.get() == 0 and self.toggle_conf.get() == 0:
            self.header_message.set("Showing all Main Switches")
            self.label.configure(text=self.header_message.get())
        elif self.toggle_mainred.get() == 1 and self.toggle_conf.get() == 0:
            self.header_message.set("Showing all Reserve Switches")
            self.label.configure(text=self.header_message.get())
        elif self.toggle_mainred.get() == 0 and self.toggle_conf.get() == 1:
            self.header_message.set("Showing Main unconfigured Switches")
            self.label.configure(text=self.header_message.get())
        elif self.toggle_mainred.get() == 1 and self.toggle_conf.get() == 1:
            self.header_message.set("Showing Reserve unconfigured Switches")
            self.label.configure(text=self.header_message.get())

        # Statusline
        total_count = len(self.tree.get_children())
        label = ttk.Label(self.status_frame, text=f"Total objects: {total_count}")
        label.grid(row=0, column=0)

    def read_config(self, file: str) -> list:
        """
        Read and parse CSV file according to buttons.

        input:
            csvfile (str)
        Outputs:
            parsed list (list)
        """
        config = []
        for row in self.config_file.read_config(file):
            if row["SW"] == "1":
                # Not configured
                if self.toggle_conf.get() == 0:
                    # Only Main
                    if self.toggle_mainred.get() == 0:
                        config.append(
                            (
                                row["Cabinet"],
                                row["AP"],
                                row["Switch IP address"],
                                row["Position"],
                            )
                        )
                    # Only Reserve
                    else:
                        if row["DIPB"] != "":
                            config.append(
                                (
                                    row["Cabinet"],
                                    row["AP"],
                                    row["Switch IP address"],
                                    row["Position"],
                                )
                            )
                # Configured
                else:
                    # Only Main
                    if self.toggle_mainred.get() == 0:
                        if row["DIPB"] != "" and row["MAC M"] == "":
                            config.append(
                                (
                                    row["Cabinet"],
                                    row["AP"],
                                    row["Switch IP address"],
                                    row["Position"],
                                )
                            )
                    # Only Reserve
                    else:
                        if row["DIPR"] != "" and row["MAC R"] == "":
                            config.append(
                                (
                                    row["Cabinet"],
                                    row["AP"],
                                    row["Switch IP address"],
                                    row["Position"],
                                )
                            )
        return config


if __name__ == "__main__":
    moxa_switch = Connection()
    app = MainApp()
