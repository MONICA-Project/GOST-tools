from tkinter import *
from GUI.gui_utilities import *
import shlex

class GetView:
    def __init__(self, main_view):
        self.view_elements = []
        self.selected_type = None
        self.selected_boolean_expression = None
        self.selected_identifiers= None
        self.result = None
        self.main_view = main_view

        main_view.current_command_view = self

        types_menu_description = Label(main_view.window, text="Select OGC entity type (mandatory field)")
        self.view_elements.append({"item":types_menu_description, "row": 1, "column": 0})

        self.selected_type = StringVar(main_view.window)
        types = {'Sensors', 'Things'}
        self.selected_type.set("Select an OGC type")

        types_menu = OptionMenu(main_view.window, self.selected_type, *types)
        self.view_elements.append({"item":types_menu, "row": 1, "column" : 1})



        selected_identifiers_description = Label(main_view.window, text="Insert one or more names or @iot.id")

        self.view_elements.append({"item":selected_identifiers_description, "row": 2, "column" : 0})
        self.selected_identifiers = Entry(main_view.window, width=10)
        self.view_elements.append({"item": self.selected_identifiers, "row": 2, "column" : 1})




        selected_boolean_expression_description = Label(main_view.window, text="Insert a filter for results\n "
                                                                               "(<,>,==,in,not in)(and or not")
        self.view_elements.append({"item":selected_boolean_expression_description, "row": 8, "column" : 0})
        self.selected_boolean_expression = Entry(main_view.window, width=10)
        self.view_elements.append({"item":self.selected_boolean_expression, "row": 8, "column" : 1})


        search_btn = Button(main_view.window, text="Search!", command=lambda: search(self))
        self.view_elements.append({"item":search_btn, "row": 10, "column" : 0})



        populate(self.view_elements)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()



def get_command(view):
    view.hide()
    GetView(view)


def search(self):
    selected_items = []
    if self.selected_type.get() == "Select an OGC type":
        result = Text(self.main_view.window, width=50, height=1)
        result.insert("1.0","Error: OGC type needed")
        result.grid(column=0, row=9)
        self.view_elements.append({"item": result, "row": 9, "column": 0})
    else:
        if bool(self.selected_identifiers.get()):
            identifiers = shlex.split(self.selected_identifiers.get())
            for i in identifiers:
                address = self.main_view.model.GOST_address + "/"
                selected_items.append(get_item(i, self.selected_type.get(),
                                           address=address))

        else:
            selected_items = get_all(self.selected_type.get())

        result = Text(self.main_view.window, width=50, height=30)
        row = 0
        for i in selected_items:
            result.insert(f"{row}.0", i)
            row += 2

        result.grid(column=0, row=9)
        self.view_elements.append({"item":result, "row": 9, "column" : 0})



