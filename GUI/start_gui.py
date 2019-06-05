from tkinter import *
from connection_config import *
from GUI.commands.get_handler import get_command
from GUI.commands.settings import change_settings
from GUI.gui_utilities import *
import copy


class Model():
    def __init__(self):
        self.GOST_address = set_GOST_address()
        self.selected_items = []


class View():
    def __init__(self):
        self.view_elements = []
        self.window = Tk()
        self.current_command_view = None
        self.model = Model()
        self.window.title("GOST-CONTROLLER")
        self.address_preview = None
        self.confirm_address_button = None
        self.new_address_entry = None

        self.window.geometry('1000x500')

        if bool(self.model.GOST_address):
            info_text = f"Current GOST address: {self.model.GOST_address}"
        else:
            info_text = "Invalid GOST address"

        self.address_preview = Button(self.window, text=f"{info_text} \nclick here to change address",
                               command=lambda: change_address_main(self))

        self.address_preview.grid(column=0, row=0)

        GET_btn = Button(self.window, text="GET", command=lambda: get_command(self))
        DELETE_btn = Button(self.window, text="DELETE")
        PATCH_btn = Button(self.window, text="PATCH")
        POST_btn = Button(self.window, text="POST")
        CREATE_btn = Button(self.window, text="CREATE on file")
        SETTINGS_btn = Button(self.window, text="SETTINGS", command=lambda: change_settings(self))

        self.main_view_elements = []

        self.main_view_elements.append({"item":GET_btn, "row":1, "column" : 1})
        self.main_view_elements.append({"item":DELETE_btn, "row":2, "column" : 1})
        self.main_view_elements.append({"item":PATCH_btn, "row":3, "column" : 1})
        self.main_view_elements.append({"item":POST_btn, "row":1, "column" : 2})
        self.main_view_elements.append({"item":CREATE_btn, "row":2, "column" : 2})
        self.main_view_elements.append({"item":SETTINGS_btn, "row":3, "column" : 2})

        populate(self.main_view_elements)

        back_button = Button(self.window, text="Back to Main Menu", command =lambda: restore_main(self))
        back_button.grid(column=3, row=0)

        self.window.mainloop()

    def hide(self):
        for i in self.main_view_elements:
            if "item" in i:
                i["item"].grid_forget()


def restore_main(self):
    self.current_command_view.hide()
    populate(self.main_view_elements)


def change_address_main(self):
    self.address_preview.configure(text="Insert a new address\n(format: http://x.x.x.x:port_number/v1.0)")

    self.new_address_entry = Entry(self.window, width=40)
    self.view_elements.append({"item": self.new_address_entry , "row": 0, "column": 1})

    self.confirm_address_button = Button(self.window, text="Confirm change",
                                         command=lambda: try_address(self))
    self.view_elements.append({"item": self.confirm_address_button, "row": 0, "column": 2})

    populate(self.view_elements)


def try_address(self):
    new_address = self.new_address_entry.get()
    working_conn = connection_config.test_connection((new_address))
    if working_conn:
        self.address_preview.configure(text=f"Current GOST address: {self.model.GOST_address} "
        f"\nclick here to change address")
        self.new_address_entry.grid_forget()
        self.confirm_address_button.grid_forget()
    else:
        self.address_preview.configure(text="Invalid address, insert a new address")


if __name__ == '__main__':
    View()
