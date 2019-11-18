import re

import GUI.gui_utilities as gui_ut
from tkinter import filedialog
from creation_utilities import create_records
from json import JSONDecoder, JSONDecodeError
import json
import ogc_utility as ogc_util


class CreateView:
    def __init__(self, main_view):
        self.view_elements = []
        self.create_values = {}
        self.create_entries = []
        self.selected_type = None
        self.save_btn = None
        self.save_and_post_btn = None
        self.number_to_create = None
        self.result = None
        self.main_view = main_view
        self.created_items = []
        self.selected_items = []
        self.post_btn = None
        self.storage_file = None
        self.post_from_file_btn = None
        self.error_message = ""

        main_view.current_command_view = self

        types_menu_description = gui_ut.Label(self.main_view.main_area, text="Select OGC entity type of the items\n"
                                                                             "you are going to create or post\n"
                                                                             "(mandatory field)")
        self.view_elements.append({"item": types_menu_description, "row": 1, "column": 0})

        self.selected_type = gui_ut.StringVar(self.main_view.main_area)
        types = gui_ut.get_ogc_types()
        self.selected_type.set("Select an OGC type")

        self.selected_type.trace("w", self.show_options)

        types_menu = gui_ut.OptionMenu(self.main_view.main_area, self.selected_type, *types)
        self.view_elements.append({"item": types_menu, "row": 1, "column": 1})

        number_to_create_description = gui_ut.Label(self.main_view.main_area, text="Select how many items create")

        self.view_elements.append({"item": number_to_create_description, "row": 2, "column": 0})
        self.number_to_create = gui_ut.Entry(self.main_view.main_area, width=10)
        self.view_elements.append({"item": self.number_to_create, "row": 2, "column": 1})

        gui_ut.populate(self.view_elements, self.main_view.main_area)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()

    def show_options(self, a, b, c):  # additional parameters a b c needed because it is called by Trace function
        if not (self.selected_type.get() == "Select an OGC type"):  # needed to avoid the restoring of action
            # buttons before action execution
            indexes_to_delete = []  # clearing the previously set patch options
            for index, val in enumerate(self.view_elements):
                if "name" in val:
                    if val["name"] in ["create_field_name", "create_field_value", "mandatory_field"]:
                        indexes_to_delete.append(index)
            for i in sorted(indexes_to_delete, reverse=True):
                self.view_elements[i]["item"].grid_forget()
                del self.view_elements[i]

            field_names = gui_ut.get_fields_names(self.selected_type.get(), needed_for_editing=True)

            row = 11

            for item in field_names:
                temp_label = gui_ut.Label(self.main_view.main_area, text=item)
                self.view_elements.append({"item": temp_label, "row": row, "column": 0, "name": "create_field_name"})
                temp_entry = gui_ut.Entry(self.main_view.main_area, width=50)
                self.view_elements.append({"item": temp_entry, "row": row, "column": 1, "name": "create_field_value"})
                row += 1
                self.create_entries.append({"field_name": item, "field_entry": temp_entry})

            self.save_btn = gui_ut.Button(self.main_view.main_area, text="Save to a file",
                                          command=lambda: save(self))
            self.view_elements.append({"item": self.save_btn, "row": 10, "column": 0, "name": "save_button"})

            self.post_btn = gui_ut.Button(self.main_view.main_area, text="Post to GOST",
                                          command=lambda: direct_post(self))
            self.view_elements.append({"item": self.post_btn, "row": 10, "column": 1, "name": "post_button"})

            self.save_and_post_btn = gui_ut.Button(self.main_view.main_area, text="Save to a file\nand Post to GOST",
                                                   command=lambda: save_and_post(self))
            self.view_elements.append({"item": self.save_and_post_btn, "row": 10, "column": 2,
                                       "name": "save_and_post_button"})
            self.post_from_file_btn = gui_ut.Button(self.main_view.main_area, text="POST records \ndefined in a file",
                                                    command=lambda: post_from_file(self))
            self.view_elements.append({"item": self.post_from_file_btn, "row": 11, "column": 2,
                                       "name": "post_from_file_button"})
            if self.selected_type.get() == "Datastreams":
                red_label = gui_ut.Label(self.main_view.main_area, text="* Fields Things_id, ObservedProperty_id, "
                                                                        "Sensor_id are mandatory", fg="#FF0000",
                                         font=(None, 15), width=60)
                self.view_elements.append(
                    {"item": red_label, "row": row, "column": 0, "name": "mandatory_field"})
            elif self.selected_type.get() == "Observations":
                red_label = gui_ut.Label(self.main_view.main_area, text="* Fields Datastream_id and FeatureOfInterest(id) "
                                                                        "are mandatory",
                                         fg="#FF0000", font=(None, 15), width=60)
                self.view_elements.append(
                    {"item": red_label, "row": row, "column": 0, "name": "mandatory_field"})
            gui_ut.populate(self.view_elements, self.main_view.main_area)


def create_command(view):
    view.back_button.grid()
    view.hide()
    CreateView(view)


def save(self):
    try:
        int(self.number_to_create.get())
    except ValueError:
        gui_ut.messagebox.showinfo("ERROR", "undefinded number\nof items to create")
    else:
        self.storage_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                                         initialdir="/", title="Select file",
                                                         filetypes=(
                                                             ("text files", "*.txt"), (".txt", "*.txt")))
        if bool(self.storage_file):
            self.created_items = create_items(self)

            if bool(self.created_items):

                for k in map(str, self.created_items["errors"]):
                    self.error_message += str(k) + " \n"

                if bool(self.error_message):
                    gui_ut.messagebox.showinfo("ERROR", self.error_message + "\nItems not created")
                elif len(self.created_items["created_items"]) > 0:
                    file_handler = open(self.storage_file, 'w')
                    for item in self.created_items["created_items"]:
                        file_handler.write(json.dumps(item) + "\n")
                    gui_ut.messagebox.showinfo("", f"Saved new items in\n{str(self.storage_file)}")
            else:
                gui_ut.messagebox.showinfo("ERROR", "Trying to create multiple items with the same name\nItems not "
                                                    "created")
    clear_before_creation(self)


def post(self):
    """Auxiliary method, used by save and post and post from file"""
    try:
        int(self.number_to_create.get())

    except ValueError:
        gui_ut.messagebox.showinfo("ERROR", "undefinded number\nof items to create")
    else:

        if bool(self.created_items):

            for k in map(str, self.created_items["errors"]):
                self.error_message += str(k) + " \n"

            if bool(self.error_message):
                gui_ut.messagebox.showinfo("ERROR", self.error_message + "\nItems not created")
            elif len(self.created_items["created_items"]) > 0:

                json_responses = []
                successful_post = False

                for item in self.created_items["created_items"]:
                    json_responses.append(ogc_util.send_json(item, ogc_name=self.selected_type.get()))
                for i in json_responses:
                    if "error" in i.json():
                        self.error_message += json.dumps((i.json())["error"]) + " \n"
                    else:
                        successful_post = True
                if bool(self.error_message):
                    gui_ut.messagebox.showinfo("ERROR", self.error_message)
                if successful_post:
                    gui_ut.messagebox.showinfo("", f"Posted new items to GOST")
                clear_before_creation(self)
        else:
            gui_ut.messagebox.showinfo("ERROR", "No items to post")

    clear_before_creation(self)


def save_and_post(self):
    try:
        int(self.number_to_create.get())

    except ValueError:
        gui_ut.messagebox.showinfo("ERROR", "undefinded number\nof items to create")
    else:
        self.storage_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                                         initialdir="/", title="Select file",
                                                         filetypes=(
                                                             ("text files", "*.txt"), (".txt", "*.txt")))
        if bool(self.storage_file):
            self.created_items = create_items(self)
            if bool(self.created_items):

                for k in map(str, self.created_items["errors"]):
                    self.error_message += str(k) + " \n"

                if bool(self.error_message):
                    gui_ut.messagebox.showinfo("ERROR", self.error_message + "\nItems not created")
                elif len(self.created_items["created_items"]) > 0:

                    file_handler = open(self.storage_file, 'w')

                    json_responses = []
                    successful_post = False

                    for item in self.created_items["created_items"]:
                        file_handler.write(json.dumps(item) + "\n")
                        json_responses.append(ogc_util.send_json(item, ogc_name=self.selected_type.get()))
                    for i in json_responses:
                        if "error" in i.json():
                            self.error_message += json.dumps((i.json())["error"]) + " \n"
                        else:
                            successful_post = True
                    if bool(self.error_message):
                        gui_ut.messagebox.showinfo("ERROR", self.error_message)

                    if successful_post:
                        gui_ut.messagebox.showinfo("", f"Saved new items in\n{str(self.storage_file)}\n"
                                                       f"and posted them to GOST")
            else:
                gui_ut.messagebox.showinfo("ERROR",
                                           "Trying to create multiple items with the same name\nItems not created")
    clear_before_creation(self)


def post_from_file(self):
    creation_result = []
    self.upload_file = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                  filetypes=(("text files", "*.txt"), (".txt", "*.txt")))

    if bool(self.upload_file):

        items_list = []  # list of the items created from file before sending, used to check for duplicate names

        with open(self.upload_file) as json_file:
            NOT_WHITESPACE = re.compile(r'[^\s]')

            def decode_stacked(document, pos=0, decoder=JSONDecoder()):
                while True:
                    match = NOT_WHITESPACE.search(document, pos)
                    if not match:
                        return
                    pos = match.start()

                    try:
                        obj, pos = decoder.raw_decode(document, pos)
                    except JSONDecodeError:
                        raise
                    yield obj

            for obj in decode_stacked(json_file.read()):
                items_list.append(obj)

            if gui_ut.check_duplicates(items_list):
                for obj in items_list:
                    result = ogc_util.add_item(obj, self.selected_type.get())
                    json_result = json.loads((result.data).decode('utf-8'))
                    creation_result.append(json_result)

                success = False

                for k in creation_result:
                    if "error" in k:
                        self.error_message += k["error"] + " \n"
                    else:
                        success = True

                if bool(self.error_message):
                    gui_ut.messagebox.showinfo("ERROR", self.error_message + "\nItems not created")

                if success:
                    gui_ut.messagebox.showinfo("", f"Posted new items to GOST")
            else:
                gui_ut.messagebox.showinfo("ERROR",
                                           "Trying to create multiple items with the same name\nItems not created")
    clear_before_creation(self)


def direct_post(self):
    try:
        int(self.number_to_create.get())

    except ValueError:
        gui_ut.messagebox.showinfo("ERROR", "undefinded number\nof items to create")
    else:
        self.created_items = create_items(self)
        if bool(self.created_items):

            for k in map(str, self.created_items["errors"]):
                self.error_message += str(k) + " \n"

            if bool(self.error_message):
                gui_ut.messagebox.showinfo("ERROR", self.error_message + "\nItems not created")
            elif len(self.created_items["created_items"]) > 0:

                json_responses = []
                successful_post = False

                for item in self.created_items["created_items"]:
                    json_responses.append(ogc_util.send_json(item, ogc_name=self.selected_type.get()))
                for i in json_responses:
                    if "error" in i.json():
                        self.error_message += json.dumps((i.json())["error"]) + " \n"
                    else:
                        successful_post = True
                if bool(self.error_message):
                    gui_ut.messagebox.showinfo("ERROR", self.error_message)
                if successful_post:
                    gui_ut.messagebox.showinfo("", f"Posted new items to GOST")
        else:
            gui_ut.messagebox.showinfo("ERROR", "Trying to create multiple items with the same name\nItems not created")
        clear_before_creation(self)


def create_items(self):
    for entry in self.create_entries:
        if bool(entry["field_entry"].get()):
            self.create_values[entry["field_name"]] = entry["field_entry"].get()
    result = (create_records(self.create_values, int(self.number_to_create.get()), self.selected_type.get()))
    if bool(result["created_items"]):
        if gui_ut.check_duplicates(result["created_items"]):
            return result
        else:
            return False
    else:
        return result


def clear_before_creation(self):
    self.create_values = {}
    self.error_message = ""
    self.create_entries = []
    self.created_items = []
    indexes_to_delete = []
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["create_field_name", "create_field_value", "save_button",
                               "post_button", "save_and_post_button", "post_from_file_button", "mandatory_field"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]
    gui_ut.populate(self.view_elements, self.main_view.main_area)
    self.selected_type.set("Select an OGC type")


def show_preview(self):
    preview = gui_ut.scrollable_results(self.created_items["created_items"], self.main_view.main_area,
                                        editable=False)
    self.view_elements.append({"item": preview, "row": 3, "column": 0, "name": "preview"})
    gui_ut.populate(self.view_elements, self.main_view.main_area)
