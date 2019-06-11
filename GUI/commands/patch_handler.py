from GUI.gui_utilities import *


class PatchView:
    def __init__(self, main_view):
        self.view_elements = []
        self.selected_type = None
        self.selected_boolean_expression = None
        self.selected_identifiers= None
        self.result = None
        self.main_view = main_view
        self.show_fields = None
        self.selected_items = None
        self.patch_btn = None
        self.abort_patch_btn = None
        self.result = None
        self.patch_values = []

        main_view.current_command_view = self

        types_menu_description = Label(main_view.main_area, text="Select OGC entity type (mandatory field)")
        self.view_elements.append({"item":types_menu_description, "row": 0, "column": 0})

        self.selected_type = StringVar(main_view.main_area)
        types = get_ogc_types()
        self.selected_type.set("Select an OGC type")

        self.selected_type.trace("w", self.show_options)

        types_menu = OptionMenu(main_view.main_area, self.selected_type, *types)
        self.view_elements.append({"item":types_menu, "row": 0, "column" : 1})

        select_introduction = Label(main_view.main_area, text="Select the items to Patch")
        self.view_elements.append({"item":select_introduction, "row": 1, "column" : 1, "name" : "select_introduction"})


        selected_identifiers_description = Label(main_view.main_area, text="Insert one or more names or @iot.id\n"
                                                                        "separated by a space\n"
                                                      "(if no item identifier is specified, all the items of "
                                                                           "selected type\nwill be selected)")

        self.view_elements.append({"item":selected_identifiers_description, "row": 2, "column" : 0,
                                   "name": "selected_identifiers_description"})
        self.selected_identifiers = Entry(main_view.main_area, width=10)
        self.view_elements.append({"item": self.selected_identifiers, "row": 2, "column" : 1,
                                   "name": "selected_identifiers"})

        selected_boolean_expression_description = Label(main_view.main_area, text="Insert a filter for results\n "
                                                                               "(<,>,==,in,not in)(and or not")
        self.view_elements.append({"item":selected_boolean_expression_description, "row": 3, "column" : 0,
                                   "name" : "selected_boolean_expression_description"})
        self.selected_boolean_expression = Entry(main_view.main_area, width=50)
        self.view_elements.append({"item":self.selected_boolean_expression, "row": 3, "column" : 1,
                                   "name": "selected_boolean_expression"})


        populate(self.view_elements, self.main_view.main_area)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()

    def show_options(self, a, b, c):  # additional parameters a b c needed because it is called by Trace function
        clear_results(self)

        self.patch_btn = Button(self.main_view.main_area, text="Patch the selected items\nwith the following values:\n"
                                                       "(empty fields will be filled with default values)",
                                                       command=lambda: patch(self), bg='#86f986')
        self.view_elements.append({"item": self.patch_btn, "row": 5, "column": 1, "name": "patching_button"})

        indexes_to_delete = []  # clearing the previously set patch options
        for index, val in enumerate(self.view_elements):
            if "name" in val:
                if val["name"] in ["patch_field_name", "patch_field_value"]:
                    indexes_to_delete.append(index)
        for i in sorted(indexes_to_delete, reverse=True):
            self.view_elements[i]["item"].grid_forget()
            del self.view_elements[i]

        field_names = get_fields_names(self.selected_type.get(), needed_for_editing=True)

        row = 7

        for item in field_names:
            temp_label = Label(self.main_view.main_area, text=item)
            self.view_elements.append({"item": temp_label, "row": row, "column": 0, "name": "patch_field_name"})
            temp_entry = Entry(self.main_view.main_area, width=50)
            self.view_elements.append({"item": temp_entry, "row": row, "column": 1, "name": "patch_field_value"})
            row += 1
            self.patch_values.append({"field_name" : item, "field_entry": temp_entry})

        populate(self.view_elements, self.main_view.main_area)


def patch_command(view):
    view.back_button.grid()
    view.hide()
    PatchView(view)


def patch(self):
    clear_results(self)

    self.selected_items = get_items(self)
    if self.selected_items != "error":
        self.result = Text(self.main_view.main_area, width=50, height=10)
        row = 0
        for i in self.selected_items:
            formatted_record = json.dumps(i, sort_keys=True, indent=2) + "\n"
            self.result.insert(f"1.0", formatted_record)
            row += 1

        self.view_elements.append({"item": self.result, "row": 1, "column": 1, "name" : "result"})
        self.patch_btn.config(text = "Click here to confirm \nthe Patching of the selected elements",
                               command = lambda : confirm_patching(self))
        self.abort_patch_btn = Button(self.main_view.main_area, text="Click here to abort the patching",
                                          command=lambda: abort_patching(self),  bg='#ff502f')
        self.view_elements.append({"item": self.abort_patch_btn, "row": 6, "column": 1,
                                   "name": "abort_patching_button"})
        populate(self.view_elements, self.main_view.main_area)

        indexes_to_delete = []  # Deleting select item fields
        for index, val in enumerate(self.view_elements):
            if "name" in val:
                if val["name"] in ["select_introduction", "selected_identifiers_description",
                                   "selected_identifiers", "selected_boolean_expression_description",
                                   "selected_boolean_expression"]:
                    indexes_to_delete.append(index)
        for i in sorted(indexes_to_delete, reverse=True):
            self.view_elements[i]["item"].grid_forget()


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

    populate(self.view_elements, self.main_view.main_area)
    messagebox.showinfo("Patch", "PATCH CONFIRMED")


def abort_patching(self):
    self.selected_items = []
    self.patch_btn.config(text="Click here to Patch the selected items\nwith the following values:\n"
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

    clear_results(self)
    populate(self.view_elements, self.main_view.main_area)
    messagebox.showinfo("Patch", "PATCH ABORTED")
