from GUI.gui_utilities import *
from tkinter import filedialog
from creation_utilities import create_records


class CreateView:
    def __init__(self, main_view):
        self.view_elements = []
        self.create_values = {}
        self.create_entries = []
        self.selected_type = None
        self.save_btn = None
        self.number_to_create = None
        self.result = None
        self.main_view = main_view
        self.created_items = []
        self.post_btn = None
        self.storage_file = None
        self.error_message = ""

        main_view.current_command_view = self

        types_menu_description = Label(main_view.window, text="Select OGC entity type of the items\n"
                                                              "you are going to create\n"
                                                              "(mandatory field)")
        self.view_elements.append({"item":types_menu_description, "row": 1, "column": 0})

        self.selected_type = StringVar(main_view.window)
        types = {'Sensors', 'Things'}
        self.selected_type.set("Select an OGC type")

        self.selected_type.trace("w", self.show_options)

        types_menu = OptionMenu(main_view.window, self.selected_type, *types)
        self.view_elements.append({"item":types_menu, "row": 1, "column" : 1})

        number_to_create_description = Label(main_view.window, text="Select how many items create")

        self.view_elements.append({"item":number_to_create_description, "row": 2, "column" : 0})
        self.number_to_create = Entry(main_view.window, width=10)
        self.view_elements.append({"item": self.number_to_create, "row": 2, "column": 1})

        populate(self.view_elements)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()

    def show_options(self, a, b, c):  # additional parameters a b c needed because it is called by Trace function

        indexes_to_delete = []  # clearing the previously set patch options
        for index, val in enumerate(self.view_elements):
            if "name" in val:
                if val["name"] in ["patch_field_name", "patch_field_value"]:
                    indexes_to_delete.append(index)
        for i in sorted(indexes_to_delete, reverse=True):
            self.view_elements[i]["item"].grid_forget()
            del self.view_elements[i]

        field_names = None
        if self.selected_type.get() == "Sensors":
            field_names = ["name", "description", "encodingType", "metadata", "Datastreams@iot.navigationLink"]
        elif self.selected_type.get() == "Things":
            field_names = ["name", "description", "properties"]

        row = 11

        for item in field_names:
            temp_label = Label(self.main_view.window, text=item)
            self.view_elements.append({"item": temp_label, "row": row, "column": 0, "name": "create_field_name"})
            temp_entry = Entry(self.main_view.window, width=50)
            self.view_elements.append({"item": temp_entry, "row": row, "column": 1, "name": "create_field_value"})
            row += 1
            self.create_entries.append({"field_name" : item, "field_entry": temp_entry})

        self.save_btn = Button(self.main_view.window, text="Save to a file",
                                                        command=lambda: save(self))
        self.view_elements.append({"item": self.save_btn, "row": 10, "column": 0, "name": "save_button"})

        self.post_btn = Button(self.main_view.window, text="Post to GOST",
                                                        command=lambda: post(self))
        self.view_elements.append({"item": self.post_btn, "row": 10, "column": 1, "name": "post_button"})

        populate(self.view_elements)


def create_command(view):
    view.hide()
    CreateView(view)


def save(self):
    try:
        int(self.number_to_create.get())

        self.storage_file = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                         filetypes=(("jpeg files", "*.txt"), ("all files", "*.*")))
        if bool(self.storage_file):
            items = create_items(self)

            self.selected_items = items["created_items"]

            for k in map(str, items["errors"]):
                self.error_message += str(k) + " \n"

            file_handler = open(self.storage_file, 'w')

            for item in self.selected_items:
                file_handler.write(json.dumps(item) + "\n")
            if bool(self.error_message):
                messagebox.showinfo("ERROR", self.error_message)
            messagebox.showinfo("", f"Saved new items in\n{str(self.storage_file)}")

    except ValueError:
        messagebox.showinfo("ERROR", "undefinded number\nof items to create")


def post(self):
    items = create_items(self)

    self.selected_items = items["created_items"]

    for k in map(str, items["errors"]):
        self.error_message += str(k) + " \n"

    file_handler = open(self.storage_file, 'w')

    for item in self.selected_items:
        file_handler.write(json.dumps(item) + "\n")


def create_items(self):
    for entry in self.create_entries:
        if bool(entry["field_entry"].get()):
            self.create_values[entry["field_name"]] = entry["field_entry"].get()
    return create_records(self.create_values, int(self.number_to_create.get()), self.selected_type.get())
