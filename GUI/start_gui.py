from tkinter import *
from connection_config import *
from GUI.commands.get_handler import get_command
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

        self.window.geometry('500x480')

        info_lbl = Label(self.window, text=f"current GOST address: {self.model.GOST_address}")

        info_lbl.grid(column=0, row=0)

        GET_btn = Button(self.window, text="GET", command=lambda: get_command(self))
        DELETE_btn = Button(self.window, text="DELETE")
        PATCH_btn = Button(self.window, text="PATCH")
        POST_btn = Button(self.window, text="POST")
        CREATE_btn = Button(self.window, text="CREATE on file")
        SETTINGS_btn = Button(self.window, text="SETTINGS")

        self.main_view_elements = []

        self.main_view_elements.append({"item":GET_btn, "row":1, "column" : 1})
        self.main_view_elements.append({"item":DELETE_btn, "row":2, "column" : 1})
        self.main_view_elements.append({"item":PATCH_btn, "row":3, "column" : 1})
        self.main_view_elements.append({"item":POST_btn, "row":1, "column" : 2})
        self.main_view_elements.append({"item":CREATE_btn, "row":2, "column" : 2})
        self.main_view_elements.append({"item":SETTINGS_btn, "row":3, "column" : 2})

        populate(self.main_view_elements)

        back_button = Button(self.window, text="Back to Main Menu", command =lambda: restore_main(self))
        back_button.grid(column=1, row=0)

        self.window.mainloop()

    def hide(self):
        for i in self.main_view_elements:
            i["item"].grid_forget()


def restore_main(self):
    self.current_command_view.hide()
    populate(self.main_view_elements)



class Controller():
    def __init__(self):
        self.root = Tk.Tk()
        self.model = Model()
        self.view = View(self.root)
        self.view.sidepanel.plotBut.bind("<Button>", self.my_plot)
        self.view.sidepanel.clearButton.bind("<Button>", self.clear)




if __name__ == '__main__':
    View()
