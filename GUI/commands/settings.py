from tkinter import *
from GUI.gui_utilities import *
import shlex


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

        change_address_description = Label(self.main_view.main_area, text=f"Insert a new address\n"
                                f"format: http://x.x.x.x:port_number/v1.0\n{current_address}")
        self.view_elements.append({"item":change_address_description, "row": 1, "column" : 0})

        self.new_address = Entry(self.main_view.main_area, width=40)
        self.view_elements.append({"item": self.new_address, "row": 1, "column" : 2})

        self.confirm_address_button = Button(self.main_view.main_area, text="Confirm change",
                                             command=lambda: change_address(self))
        self.view_elements.append({"item": self.confirm_address_button, "row": 1, "column" : 3})

        populate(self.view_elements)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()


def change_settings(view):
    view.back_button.grid()
    view.hide()
    SettingsView(view)


def change_address(self):
    new_address = self.new_address.get()
    working_conn = connection_config.test_connection((new_address))
    if working_conn:

        self.main_view.model.GOST_address = new_address

        connection_config.set_GOST_address(new_address)  # saving the new address works

        self.main_view.address_preview.configure(text=f"Current GOST address: {self.main_view.model.GOST_address} "
                                                      f"\nclick here to change address")
        self.confirm_address_button.configure(text="To change address, insert a new address\nand click here")
        if bool(self.main_view.confirm_address_button):
            self.main_view.confirm_address_button.grid_forget()
            self.main_view.new_address_entry.grid_forget()
    else:
        self.confirm_address_button.configure(text="Invalid address, insert a new address\nand click here")


