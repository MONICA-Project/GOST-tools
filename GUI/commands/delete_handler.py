from tkinter import *
from GUI.gui_utilities import *
import shlex


class DeleteView:
    def __init__(self, main_view):
        self.view_elements = []
        self.selected_type = None
        self.selected_boolean_expression = None
        self.selected_identifiers= None
        self.result = None
        self.main_view = main_view
        self.show_fields = "all"
        self.selected_items = None
        self.delete_btn = None
        self.result = None

        main_view.current_command_view = self

        types_menu_description = Label(main_view.window, text="Select OGC entity type (mandatory field)")
        self.view_elements.append({"item":types_menu_description, "row": 1, "column": 0})

        self.selected_type = StringVar(main_view.window)
        types = {'Sensors', 'Things'}
        self.selected_type.set("Select an OGC type")

        self.selected_type.trace("w", self.show_options)

        types_menu = OptionMenu(main_view.window, self.selected_type, *types)
        self.view_elements.append({"item":types_menu, "row": 1, "column" : 1})

        selected_identifiers_description = Label(main_view.window, text="Insert one or more names or @iot.id\n"
                                                                        "separated by a space")

        self.view_elements.append({"item":selected_identifiers_description, "row": 2, "column" : 0})
        self.selected_identifiers = Entry(main_view.window, width=10)
        self.view_elements.append({"item": self.selected_identifiers, "row": 2, "column" : 1})

        selected_boolean_expression_description = Label(main_view.window, text="Insert a filter for results\n "
                                                                               "(<,>,==,in,not in)(and or not")
        self.view_elements.append({"item":selected_boolean_expression_description, "row": 7, "column" : 0})
        self.selected_boolean_expression = Entry(main_view.window, width=50)
        self.view_elements.append({"item":self.selected_boolean_expression, "row": 7, "column" : 1})

        fields_menu_description = Label(main_view.window, text="Select fields to show (default: all)")
        self.view_elements.append({"item":fields_menu_description, "row": 8, "column": 0})

        self.delete_btn = Button(main_view.window, text="Delete", command=lambda: delete(self))
        self.view_elements.append({"item": self.delete_btn, "row": 10, "column": 1})

        populate(self.view_elements)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()

    def show_options(self, a, b, c):  # additional parameters a b c needed because it is called by Trace function
        field_names = None
        if self.selected_type.get() == "Sensors":
            field_names = ["name", "description", "encodingType", "metadata", "Datastreams@iot.navigationLink"]
        elif self.selected_type.get() == "Things":
            field_names = ["name", "description", "properties"]

        self.show_fields = Listbox(self.main_view.window, selectmode=MULTIPLE)

        self.show_fields.insert(END, "@iot.id")

        for item in field_names:
            self.show_fields.insert(END, item)

        self.show_fields.grid(column=1, row=8)
        self.view_elements.append({"item": self.show_fields, "row": 9, "column": 0, "name": "show_fields"})


def delete_command(view):
    view.hide()
    DeleteView(view)


def delete(self):
    clear_results(self)

    self.selected_items = get_items(self)
    if self.selected_items != "error":
        self.result = Text(self.main_view.window, width=50, height=10)
        row = 0
        for i in self.selected_items:
            formatted_record = json.dumps(i, sort_keys=True, indent=2) + "\n"
            self.result.insert(f"1.0", formatted_record)
            row += 1

        self.view_elements.append({"item": self.result, "row": 9, "column": 1, "name" : "result"})
        self.delete_btn.config(text = "Click here to confirm \nthe deletion of the selected elements",
                               command = lambda : confirm_deletion(self))
        self.abort_delete_button = Button(self.main_view.window, text="Click here to abort the deletion",
                                          command=lambda: abort_deletion(self))
        self.view_elements.append({"item": self.abort_delete_button, "row": 10, "column": 3,
                                   "name": "abort_deletion_button"})
        populate(self.view_elements)


def confirm_deletion(self):
    address = self.main_view.model.GOST_address + "/"
    for i in self.selected_items:
        if "@iot.id" in i:
            delete_item(i["@iot.id"], self.selected_type.get(), address=address)

    self.delete_btn.config(text="Delete",
                           command=lambda: delete(self))
    self.selected_items = []
    indexes_to_delete = []
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["abort_deletion_button", "result", "show_fields"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]
    messagebox.showinfo("Delete", "DELETION CONFIRMED")



def abort_deletion(self):
    self.selected_items = []
    self.delete_btn.config(text="Delete",
                           command=lambda: delete(self))
    indexes_to_delete = []
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["abort_deletion_button", "result", "show_fields"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]
