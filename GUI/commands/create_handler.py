from GUI.gui_utilities import *


class CreateView:
    def __init__(self, main_view):
        self.view_elements = []
        self.selected_type = None
        self.selected_boolean_expression = None
        self.selected_identifiers= None
        self.result = None
        self.main_view = main_view
        self.show_fields = "all"
        self.selected_items = None
        self.patch_btn = None
        self.abort_patch_btn = None
        self.result = None
        self.patch_values = []

        main_view.current_command_view = self

        types_menu_description = Label(main_view.window, text="Select OGC entity type to create\n"
                                                              "(mandatory field)")
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

        self.patch_btn = Button(main_view.window, text="Click here to Patch\nwith the following values:\n"
                                                       "(an ogc entity type must be selected)",
                                                        command=lambda: patch(self))
        self.view_elements.append({"item": self.patch_btn, "row": 10, "column": 1, "name": "patching_button"})

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

        self.show_fields = Listbox(self.main_view.window, selectmode=MULTIPLE)

        self.show_fields.insert(END, "@iot.id")

        row = 11

        for item in field_names:

            self.show_fields.insert(END, item)
            if item != "name":
                temp_label = Label(self.main_view.window, text=item)
                self.view_elements.append({"item": temp_label, "row": row, "column": 0, "name": "patch_field_name"})
                temp_entry = Entry(self.main_view.window, width=50)
                self.view_elements.append({"item": temp_entry, "row": row, "column": 1, "name": "patch_field_value"})
                row += 1
                self.patch_values.append({"field_name" : item, "field_entry": temp_entry})

        self.show_fields.grid(column=1, row=8)
        self.view_elements.append({"item": self.show_fields, "row": 9, "column": 0, "name": "show_fields"})

        populate(self.view_elements)


def create_command(view):
    view.hide()
    CreateView(view)


def patch(self):
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
        self.patch_btn.config(text = "Click here to confirm \nthe Patching of the selected elements",
                               command = lambda : confirm_patching(self))
        self.abort_patch_btn = Button(self.main_view.window, text="Click here to abort the patching",
                                          command=lambda: abort_patching(self))
        self.view_elements.append({"item": self.abort_patch_btn, "row": 10, "column": 3,
                                   "name": "abort_patching_button"})
        populate(self.view_elements)


def confirm_patching(self):
    address = self.main_view.model.GOST_address + "/"
    patches = {}
    for i in self.patch_values:
        if bool(i["field_entry"].get()):
            patches[i["field_name"]] = i["field_entry"].get()
    for i in self.selected_items:
        if "@iot.id" in i:
            patch_item(patches, str(i.get("@iot.id")), self.selected_type.get(), address=address)

    self.patch_btn.config(text="Click here to Patch\nwith the following values:\n"
                                "(an ogc entity type must be selected)",
                                command=lambda: patch(self))
    self.selected_items = []
    indexes_to_delete = []
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["abort_patching_button", "result", "show_fields"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]
    messagebox.showinfo("Patch", "PATCH CONFIRMED")


def abort_patching(self):
    self.selected_items = []
    self.patch_btn.config(text="Click here to Patch\nwith the following values:\n"
                                "(an ogc entity type must be selected)",
                           command=lambda: patch(self))
    indexes_to_delete = []
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["abort_patching_button", "result", "show_fields"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]
