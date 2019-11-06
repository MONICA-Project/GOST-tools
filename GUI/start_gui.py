from tkinter.font import Font
import connection_config as conn_conf
from GUI.commands.get_handler import get_command
from GUI.commands.delete_handler import delete_command
from GUI.commands.patch_handler import patch_command
from GUI.commands.create_handler import create_command
from GUI.commands.settings import change_settings, ping_connection
import GUI.gui_utilities as gui_ut
import GUI.scrollbar as scroll


class Model:
    def __init__(self):
        self.GOST_address = conn_conf.set_GOST_address()
        self.selected_items = []


class View:
    def __init__(self):
        self.view_elements = []
        self.window = gui_ut.Tk()
        self.width = 1000
        self.height = 600
        self.current_command_view = None
        self.model = Model()
        self.window.title("GOST-CONTROLLER")

        self.window.geometry(f'{str(self.width)}x{str(self.height)}')

        # setting the general layout

        self.top_bar = gui_ut.Frame(self.window, width=self.width, bg="#ababab")
        main_area_frame = gui_ut.Frame(self.window, width=self.width, bg="#ababab")
        self.main_area = scroll.Scrollable(main_area_frame, width=16)
        self.top_bar.pack(side="top", fill="both")
        main_area_frame.pack(side="top", fill="both", expand=True)

        self.address_preview = None
        self.confirm_address_button = None
        self.new_address_entry = None
        self.keep_old_address_button = None
        self.back_button = None

        if bool(self.model.GOST_address):
            info_text = f"Current GOST address: {self.model.GOST_address}"
        else:
            info_text = "Invalid GOST address"

        self.address_preview = gui_ut.Button(self.top_bar, text=f"{info_text} \nclick here to change address",
                                             command=lambda: change_address_main(self), bg=gui_ut.change_address_color)
        self.port_button = gui_ut.Button(self.top_bar, text="Change port number",
                                         command=lambda: change_port_number(self), bg=gui_ut.change_address_color)
        self.ping_button = gui_ut.Button(self.top_bar, text="Ping Connection",
                                         command=lambda: ping_connection(self, self.model.GOST_address, True),
                                         bg=gui_ut.change_address_color)
        self.ping_button.grid(row=0, column=5)
        self.address_preview.grid(row=0, column=0)
        self.port_button.grid(row=0, column=4)

        button_height = int(int(self.height) / 99)
        button_width = int(int(self.width) / 40)

        myFont = Font(family='Helvetica', size=20, weight='bold')

        GET_btn = gui_ut.Button(self.main_area, text="GET", height=button_height, width=button_width,
                                command=lambda: get_command(self), bg='#86f986')
        GET_btn["font"] = myFont

        DELETE_btn = gui_ut.Button(self.main_area, height=button_height, width=button_width,
                                   text="DELETE", command=lambda: delete_command(self), bg='#f17e7e')
        DELETE_btn["font"] = myFont

        PATCH_btn = gui_ut.Button(self.main_area, text="PATCH", command=lambda: patch_command(self), bg='#efca8c')
        PATCH_btn["font"] = myFont

        CREATE_btn = gui_ut.Button(self.main_area, text="CREATE/POST", height=button_height, width=button_width,
                                   command=lambda: create_command(self), bg='#9ea9f0')
        CREATE_btn["font"] = myFont

        SETTINGS_btn = gui_ut.Button(self.main_area, text="SETTINGS", command=lambda: change_settings(self),
                                     bg='#fff1c1')
        SETTINGS_btn["font"] = myFont

        self.main_view_elements = []

        self.main_view_elements.append({"item": GET_btn, "row": 0, "column": 0})
        self.main_view_elements.append({"item": DELETE_btn, "row": 1, "column": 0})
        self.main_view_elements.append({"item": PATCH_btn, "row": 0, "column": 1})
        self.main_view_elements.append({"item": CREATE_btn, "row": 1, "column": 1})
        self.main_view_elements.append({"item": SETTINGS_btn, "row": 2, "column": 0})

        self.main_area.columnconfigure(0, weight=1)
        self.main_area.columnconfigure(1, weight=1)
        self.main_area.rowconfigure(0, weight=1)
        self.main_area.rowconfigure(1, weight=1)
        self.main_area.rowconfigure(2, weight=1)
        self.main_area.rowconfigure(3, weight=1)

        gui_ut.populate(self.main_view_elements, self.main_area)

        self.back_button = gui_ut.Button(self.top_bar, text="Back to Main Menu", command=lambda: restore_main(self),
                                         bg='#ff502f')
        self.back_button.grid(row=0, column=6, sticky=gui_ut.N + gui_ut.S)
        self.back_button.grid_remove()

        self.window.mainloop()

    def hide(self):
        for i in self.main_view_elements:
            if "item" in i:
                i["item"].grid_forget()


def restore_main(self):
    self.back_button.grid_remove()
    if bool(self.current_command_view):
        self.current_command_view.hide()
    gui_ut.reset_attribute(self,
                           ["selected_items", "selected_type", "selected_boolean_expression", "selected_identifiers",
                            "show_fields", "patch_values", "create_values", "create_entries", "created_items",
                            "storage_file"])
    gui_ut.populate(self.main_view_elements)


def change_address_main(self):
    # self.address_preview.configure(text="Insert a new address\n(format: http[s]://x.x.x.x:port_number/v1.0)")
    self.new_address_entry = gui_ut.Entry(self.top_bar, width=40)
    self.new_address_entry.insert(0, string=self.model.GOST_address)
    self.view_elements.append({"item": self.new_address_entry, "row": 0, "column": 1, "name": "new_address_entry"})

    self.confirm_address_button = gui_ut.Button(self.top_bar, text="Confirm changes",
                                                command=lambda: try_address(self))
    self.view_elements.append({"item": self.confirm_address_button, "row": 0, "column": 2,
                               "name": "new_address_button"})

    self.keep_old_address_button = gui_ut.Button(self.top_bar, text="Keep old address",
                                                 command=lambda: keep_address(self))
    self.view_elements.append({"item": self.keep_old_address_button, "row": 0, "column": 3,
                               "name": "keep_old_address_button"})
    self.new_address_entry.grid(row=0, column=1)
    self.confirm_address_button.grid(row=0, column=2)
    self.keep_old_address_button.grid(row=0, column=3)
    gui_ut.populate(self.view_elements, self.main_area)


def try_address(self):
    new_address = self.new_address_entry.get()  # checking if the new address works
    working_conn = conn_conf.test_connection(new_address)
    if working_conn:
        self.model.GOST_address = new_address

        conn_conf.set_GOST_address(new_address)  # saving the new address works

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
        gui_ut.messagebox.showinfo("Error", "invalid GOST address")
        self.address_preview.configure(text="Invalid address, insert a new address")


def keep_address(self):
    self.model.GOST_address = conn_conf.set_GOST_address()
    if bool(self.model.GOST_address):
        self.address_preview.configure(text=f"Current GOST address: {self.model.GOST_address} "
                                            f"\nclick here to change address")
    else:
        self.address_preview.configure(text=f"Current GOST address not working"
                                            f"\nclick here to change address\n"
                                            f"or retry to connect with the last saved address")
    indexes_to_delete = []
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["new_address_entry", "new_address_button", "keep_old_address_button"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]


def change_port_number(self):
    self.port_button.grid_forget()
    # self.address_preview.configure(text="Insert a new port number")

    self.new_port_entry = gui_ut.Entry(self.top_bar, width=40)
    self.new_port_entry.insert(0, string=conn_conf.try_port(take=1))
    self.view_elements.append({"item": self.new_port_entry, "row": 0, "column": 1, "name": "new_port_entry"})

    self.confirm_port_button = gui_ut.Button(self.top_bar, text="Confirm changes",
                                             command=lambda: conn_conf.try_port(self, self.new_port_entry.get()))
    self.view_elements.append({"item": self.confirm_port_button, "row": 0, "column": 2,
                               "name": "new_port_button"})
    self.new_port_entry.grid(row=0, column=1)
    self.confirm_port_button.grid(row=0, column=2)
    self.address_preview.configure(text=f"Current GOST address: {self.model.GOST_address} "
                                        f"\nclick here to change address")
    gui_ut.populate(self.view_elements, self.main_area)


if __name__ == '__main__':
    View()
