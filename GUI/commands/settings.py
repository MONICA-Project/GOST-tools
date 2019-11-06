from tkinter import *
import GUI.gui_utilities as gui_ut
import shlex
import connection_config as conn_conf


class SettingsView:
    def __init__(self, main_view):
        self.view_elements = []
        self.main_view = main_view
        self.confirm_address_button = None

        main_view.current_command_view = self  # needed for hide() function to work on the current elements

        if bool(main_view.model.GOST_address):
            current_address = f"[Current GOST address: {self.main_view.model.GOST_address}]"
        else:
            current_address = "[Current GOST address is not working]"

        self.change_address_description = Label(self.main_view.main_area, text=f"Insert a new address\n"
                                f"format: http://x.x.x.x:port_number/v1.0\n{current_address}")
        self.view_elements.append({"item": self.change_address_description, "row": 1, "column": 0})
        self.change_port_description = Label(self.main_view.main_area, text=f"Insert a new port")
        self.view_elements.append({"item": self.change_port_description, "row": 3, "column": 0})
        self.new_port = Entry(self.main_view.main_area, width=40)
        self.new_port.insert(0, conn_conf.try_port(take=1))
        self.new_address = Entry(self.main_view.main_area, width=40)
        self.new_address.insert(0, self.main_view.model.GOST_address)
        self.view_elements.append({"item": self.new_address, "row": 1, "column": 2})
        self.view_elements.append({"item": self.new_port, "row": 3, "column": 2})
        self.confirm_address_button = gui_ut.Button(self.main_view.main_area, text="Confirm change",
                                             command=lambda: change_address(self), bg=gui_ut.action_color)
        self.view_elements.append({"item": self.confirm_address_button, "row": 1, "column": 3})
        self.confirm_port_button = gui_ut.Button(self.main_view.main_area, text="Confirm change",
                                             command=lambda: conn_conf.try_port(self, self.new_port.get(), b=1), bg=gui_ut.action_color)
        self.view_elements.append({"item": self.confirm_port_button, "row": 3, "column": 3})
        self.ping_button = gui_ut.Button(self.main_view.main_area, text="Ping Connection",
                                             command=lambda: ping_connection(self, self.main_view.model.GOST_address), bg=gui_ut.action_color)
        self.view_elements.append({"item": self.ping_button, "row": 4, "column": 0})
        gui_ut.populate(self.view_elements)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()


def ping_connection(self, gost_address, b=FALSE):
    if b:
        if conn_conf.test_connection(gost_address):
            gui_ut.messagebox.showinfo("OK", "Server is reachable at " + gost_address)
        else:
            gui_ut.messagebox.showinfo("Error", "Address" + gost_address + "is not valid!")
    else:
        if conn_conf.test_connection(gost_address):
            gui_ut.messagebox.showinfo("OK", "Server is reachable at " + gost_address)
        else:
            gui_ut.messagebox.showinfo("Error", "Address" + gost_address + "is not valid!")


def change_settings(view):
    view.back_button.grid()
    view.hide()
    SettingsView(view)


def change_address(self):
    new_address = self.new_address.get()
    working_conn = conn_conf.test_connection(new_address)
    if working_conn:

        self.main_view.model.GOST_address = new_address

        conn_conf.set_GOST_address(new_address)  # saving the new address works

        self.main_view.address_preview.configure(text=f"Current GOST address: {self.main_view.model.GOST_address} "
                                                      f"\nclick here to change address")
        self.confirm_address_button.configure(text="To change address, insert a new address\nand click here")
        if bool(self.main_view.confirm_address_button):
            self.main_view.confirm_address_button.grid_forget()
            self.main_view.new_address_entry.grid_forget()
    else:
        self.confirm_address_button.configure(text="Invalid address, insert a new address\nand click here")


