from tkinter import messagebox
from connection_config import *
from GUI.commands.get_handler import get_command
from GUI.commands.delete_handler import delete_command
from GUI.commands.patch_handler import patch_command
from GUI.commands.settings import change_settings
from GUI.gui_utilities import *


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
        self.keep_old_address_button = None

        self.window.geometry('1000x600')

        if bool(self.model.GOST_address):
            info_text = f"Current GOST address: {self.model.GOST_address}"
        else:
            info_text = "Invalid GOST address"

        self.address_preview = Button(self.window, text=f"{info_text} \nclick here to change address",
                               command=lambda: change_address_main(self))

        self.address_preview.grid(column=0, row=0)

        GET_btn = Button(self.window, text="GET", command=lambda: get_command(self))
        DELETE_btn = Button(self.window, text="DELETE", command=lambda: delete_command(self))
        PATCH_btn = Button(self.window, text="PATCH", command=lambda: patch_command(self))
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
        back_button.grid(column=4, row=0)

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
    self.view_elements.append({"item": self.new_address_entry, "row": 0, "column": 1, "name": "new_address_entry"})

    self.confirm_address_button = Button(self.window, text="Confirm change",
                                         command=lambda: try_address(self))
    self.view_elements.append({"item": self.confirm_address_button, "row": 0, "column": 2,
                               "name": "new_address_button"})

    self.keep_old_address_button = Button(self.window, text="Keep old address",
                                         command=lambda: keep_address(self))
    self.view_elements.append({"item": self.keep_old_address_button, "row": 0, "column": 3,
                               "name": "keep_old_address_button"})


    populate(self.view_elements)


def try_address(self):
    new_address = self.new_address_entry.get()
    working_conn = connection_config.test_connection((new_address))
    if working_conn:
        self.address_preview.configure(text=f"Current GOST address: {self.model.GOST_address} "
        f"\nclick here to change address")
        indexes_to_delete = []
        for index, val in enumerate(self.view_elements):
            if "name" in val:
                if val["name"] in ["new_address_entry", "new_address_button", "keep_old_address_button"]:
                    indexes_to_delete.append(index)
        for i in sorted(indexes_to_delete, reverse=True):
            self.view_elements[i]["item"].grid_forget()
            del self.view_elements[i]

    else:
        messagebox.showinfo("Error", "invalid GOST address")
        self.address_preview.configure(text="Invalid address, insert a new address")


def keep_address(self):
    self.address_preview.configure(text=f"Current GOST address: {self.model.GOST_address} "
    f"\nclick here to change address")
    indexes_to_delete = []
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["new_address_entry", "new_address_button", "keep_old_address_button"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]


if __name__ == '__main__':
    View()
