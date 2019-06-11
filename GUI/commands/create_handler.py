from GUI.gui_utilities import *
from tkinter import filedialog
from creation_utilities import create_records
from json import JSONDecoder, JSONDecodeError


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

        types_menu_description = Label(self.main_view.main_area, text="Select OGC entity type of the items\n"
                                                              "you are going to create or post\n"
                                                              "(mandatory field)")
        self.view_elements.append({"item":types_menu_description, "row": 1, "column": 0})

        self.selected_type = StringVar(self.main_view.main_area)
        types = get_ogc_types()
        self.selected_type.set("Select an OGC type")

        self.selected_type.trace("w", self.show_options)

        types_menu = OptionMenu(self.main_view.main_area, self.selected_type, *types)
        self.view_elements.append({"item":types_menu, "row": 1, "column" : 1})

        number_to_create_description = Label(self.main_view.main_area, text="Select how many items create")

        self.view_elements.append({"item":number_to_create_description, "row": 2, "column" : 0})
        self.number_to_create = Entry(self.main_view.main_area, width=10)
        self.view_elements.append({"item": self.number_to_create, "row": 2, "column": 1})

        populate(self.view_elements, self.main_view.main_area)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()

    def show_options(self, a, b, c):  # additional parameters a b c needed because it is called by Trace function

        indexes_to_delete = []  # clearing the previously set patch options
        for index, val in enumerate(self.view_elements):
            if "name" in val:
                if val["name"] in ["create_field_name", "create_field_value"]:
                    indexes_to_delete.append(index)
        for i in sorted(indexes_to_delete, reverse=True):
            self.view_elements[i]["item"].grid_forget()
            del self.view_elements[i]

        field_names = get_fields_names(self.selected_type.get(), needed_for_editing=True)

        row = 11

        for item in field_names:
            temp_label = Label(self.main_view.main_area, text=item)
            self.view_elements.append({"item": temp_label, "row": row, "column": 0, "name": "create_field_name"})
            temp_entry = Entry(self.main_view.main_area, width=50)
            self.view_elements.append({"item": temp_entry, "row": row, "column": 1, "name": "create_field_value"})
            row += 1
            self.create_entries.append({"field_name" : item, "field_entry": temp_entry})

        self.save_btn = Button(self.main_view.main_area, text="Save to a file",
                                                        command=lambda: save(self))
        self.view_elements.append({"item": self.save_btn, "row": 10, "column": 0, "name": "save_button"})

        self.post_btn = Button(self.main_view.main_area, text="Post to GOST",
                                                        command=lambda: post(self))
        self.view_elements.append({"item": self.post_btn, "row": 10, "column": 1, "name": "post_button"})

        self.save_and_post_btn = Button(self.main_view.main_area, text="Save to a file\nand Post to GOST",
                               command=lambda: save_and_post(self))
        self.view_elements.append({"item": self.save_and_post_btn, "row": 10, "column": 2,
                                   "name": "save_and_post_button"})
        self.post_from_file_btn = Button(self.main_view.main_area, text="POST records \ndefined in a file",
                                        command=lambda: post_from_file(self))
        self.view_elements.append({"item": self.post_from_file_btn, "row": 10, "column": 3,
                                   "name": "save_and_post_button"})

        populate(self.view_elements, self.main_view.main_area)


def create_command(view):
    view.back_button.grid()
    view.hide()
    CreateView(view)


def save(self):
    try:
        int(self.number_to_create.get())
        if not bool(self.created_items):
            self.created_items = create_items(self)

        for k in map(str, self.created_items["errors"]):
            self.error_message += str(k) + " \n"

        if bool(self.error_message):
            messagebox.showinfo("ERROR", self.error_message + "\nItems not created")
        elif len(self.created_items["created_items"]) > 0:

            self.storage_file = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                             filetypes=(
                                                             ("text files", "*.txt"), ("text files", "*.txt")))
            file_handler = open(self.storage_file, 'w')
            for item in self.created_items["created_items"]:
                file_handler.write(json.dumps(item) + "\n")
            messagebox.showinfo("", f"Saved new items in\n{str(self.storage_file)}")
            clear_before_creation(self)

    except ValueError:
        messagebox.showinfo("ERROR", "undefinded number\nof items to create")


def post(self):
    try:
        int(self.number_to_create.get())

        if not bool(self.created_items):
            self.created_items = create_items(self)

        for k in map(str, self.created_items["errors"]):
            self.error_message += str(k) + " \n"

        if bool(self.error_message):
            messagebox.showinfo("ERROR", self.error_message + "\nItems not created")
        elif len(self.created_items["created_items"]) > 0:

            for item in self.created_items["created_items"]:
                send_json(item, ogc_name=self.selected_type.get())
            messagebox.showinfo("", f"Posted new items to GOST")
            clear_before_creation(self)

    except ValueError:
        messagebox.showinfo("ERROR", "undefinded number\nof items to create")


def save_and_post(self):
    try:
        int(self.number_to_create.get())
        if not bool(self.created_items):
            self.created_items = create_items(self)

        for k in map(str, self.created_items["errors"]):
            self.error_message += str(k) + " \n"

        if bool(self.error_message):
            messagebox.showinfo("ERROR", self.error_message + "\nItems not created")
        elif len(self.created_items["created_items"]) > 0:

            self.storage_file = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                             filetypes=(
                                                             ("jpeg files", "*.txt"), ("all files", "*.*")))
            file_handler = open(self.storage_file, 'w')
            for item in self.created_items["created_items"]:
                file_handler.write(json.dumps(item) + "\n")
                send_json(item, ogc_name=self.selected_type.get())
            messagebox.showinfo("", f"Saved new items in\n{str(self.storage_file)}\n"
                                f"and posted them to GOST")
            clear_before_creation(self)

    except ValueError:
        messagebox.showinfo("ERROR", "undefinded number\nof items to create")


def post_from_file(self):
    creation_result = []
    self.upload_file = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                     filetypes=(
                                                     ("jpeg files", "*.txt"), ("all files", "*.*")))
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
            result = add_item(obj, self.selected_type.get())
            json_result = json.loads((result.data).decode('utf-8'))
            creation_result.append(json_result)

    success = False

    for k in creation_result:
        if "error" in k:
            self.error_message += k["error"] + " \n"
        else:
            success = True

    if bool(self.error_message):
        messagebox.showinfo("ERROR", self.error_message + "\nItems not created")

    if success:
        messagebox.showinfo("", f"Posted new items to GOST")
    clear_before_creation(self)




def create_items(self):
    for entry in self.create_entries:
        if bool(entry["field_entry"].get()):
            self.create_values[entry["field_name"]] = entry["field_entry"].get()
    return create_records(self.create_values, int(self.number_to_create.get()), self.selected_type.get())


def clear_before_creation(self):
    self.create_values = {}
    self.error_message = []
    self.create_entries = []
    self.created_items = []


    indexes_to_delete = []
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["create_field_name", "create_field_value", "save_button",
                               "post_button", "save_and_post_button"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]
