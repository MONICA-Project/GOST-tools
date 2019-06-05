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
        self.show_fields = "all"

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

        types_menu_description = Label(main_view.window, text="Select fields to show (default: all)")
        self.view_elements.append({"item":types_menu_description, "row": 8, "column": 0})

        search_btn = Button(main_view.window, text="Search!", command=lambda: search(self))
        self.view_elements.append({"item":search_btn, "row": 10, "column" : 0})

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
        self.view_elements.append({"item": self.show_fields, "row": 9, "column": 0})


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

        if bool(self.selected_boolean_expression.get()):  # filtering the results
            expression = shlex.split(self.selected_boolean_expression.get())
            for single_item in selected_items.copy():
                matching = selection_parser.select_parser(expression, single_item)
                if not matching:
                    selected_items.remove(single_item)
                elif isinstance(matching, dict):
                    if "error" in matching:
                        selected_items.remove(single_item)
            if len(selected_items) == 0:
                selected_items += [f"error: no items found with select statement conditions"]

        if len(self.show_fields.curselection()) > 0:
            selected_fields_names = [self.show_fields.get(i) for i in self.show_fields.curselection()]
            temporary_selected_items = []
            for i in selected_items:
                if "error" in i:
                    temporary_selected_items.append(copy.deepcopy(i))
                else:
                    temporary_item = copy.deepcopy(i)
                    for key in i:
                        if key not in selected_fields_names:
                            temporary_item.pop(key)
                    temporary_selected_items.append(temporary_item)
            selected_items = temporary_selected_items

        result = Text(self.main_view.window, width=50, height=10)
        row = 0
        for i in selected_items:
            formatted_record = json.dumps(i, sort_keys=True, indent=2) + "\n"
            result.insert(f"1.0", formatted_record)
            row += 1

        result.grid(column=0, row=9)
        self.view_elements.append({"item":result, "row": 9, "column" : 0})



