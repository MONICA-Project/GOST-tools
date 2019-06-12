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

        types_menu_description = Label(main_view.main_area, borderwidth=2, relief="solid",
                                       text="Select OGC entity type (mandatory field)")
        self.view_elements.append({"item":types_menu_description, "row": 1, "column": 0})

        self.selected_type = StringVar(main_view.main_area)
        types = get_ogc_types()
        self.selected_type.set("Select an OGC type")

        self.selected_type.trace("w", self.show_options)

        types_menu = OptionMenu(main_view.main_area, self.selected_type, *types)
        self.view_elements.append({"item":types_menu, "row": 1, "column" : 1})

        selected_identifiers_description = Label(main_view.main_area, borderwidth=2, relief="solid",
                                                 text=select_id_text)

        self.view_elements.append({"item":selected_identifiers_description, "row": 2, "column" : 0})
        self.selected_identifiers = Entry(main_view.main_area, width=10)
        self.view_elements.append({"item": self.selected_identifiers, "row": 2, "column" : 1})

        selected_boolean_expression_description = Label(main_view.main_area, borderwidth=2, relief="solid",
                                                        text=select_conditions_text)

        self.view_elements.append({"item":selected_boolean_expression_description, "row": 7, "column" : 0})
        self.selected_boolean_expression = Entry(main_view.main_area, width=50)
        self.view_elements.append({"item":self.selected_boolean_expression, "row": 7, "column" : 1})

        fields_menu_description = Label(main_view.main_area, borderwidth=2, relief="solid",
                                        text="Select fields to show\n"
                                             "of the items you are going to delete (default: all)")
        self.view_elements.append({"item":fields_menu_description, "row": 8, "column": 0})

        populate(self.view_elements, self.main_view.main_area)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()

    def show_options(self, a, b, c):  # additional parameters a b c needed because it is called by Trace function
        clear_results(self)

        field_names = get_fields_names(self.selected_type.get())

        self.show_fields = Listbox(self.main_view.main_area, selectmode=MULTIPLE)

        self.show_fields.insert(END, "@iot.id")

        for item in field_names:
            self.show_fields.insert(END, item)

        self.show_fields.grid(column=1, row=8)
        self.view_elements.append({"item": self.show_fields, "row": 9, "column": 0, "name": "show_fields"})

        self.delete_btn = Button(self.main_view.main_area, text="Delete", command=lambda: delete(self),
                                 bg='#ff502f')
        self.view_elements.append({"item": self.delete_btn, "row": 10, "column": 1, "name" : "delete_button"})

        populate(self.view_elements, self.main_view.main_area)


def delete_command(view):
    view.back_button.grid()
    view.hide()
    DeleteView(view)


def delete(self):
    clear_results(self)

    self.selected_items = get_items(self)
    if bool(self.selected_items):
        if self.selected_items != "error":
            self.result = scrollable_results(self.selected_items, self.main_view.main_area)

            self.view_elements.append({"item": self.result, "row": 9, "column": 1, "name" : "result"})
            self.delete_btn.config(text = "Click here to confirm",
                                   command = lambda : confirm_deletion(self),   bg=confirm_color)
            self.abort_delete_button = Button(self.main_view.main_area, text="Click here to abort the delete",
                                              command=lambda: abort_deletion(self), bg=abort_color)
            self.view_elements.append({"item": self.abort_delete_button, "row": 11, "column": 1,
                                       "name": "abort_deletion_button"})
            populate(self.view_elements, self.main_view.main_area)
    else:
        messagebox.showinfo("Error", "NO ITEMS FOUND")


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

    messagebox.showinfo("Delete", "DELETE CONFIRMED")
    self.selected_type.set("Select an OGC type")
    hide_delete_button(self)



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
    self.selected_type.set("Select an OGC type")
    hide_delete_button(self)


def hide_delete_button(self):
    for i in self.view_elements:
        if "name" in i:
            if i["name"] == "delete_button":
                i["item"].grid_forget()