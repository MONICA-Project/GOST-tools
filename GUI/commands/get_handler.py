from GUI.gui_utilities import *


class GetView:
    def __init__(self, main_view):
        self.view_elements = []
        self.selected_type = None
        self.selected_boolean_expression = None
        self.selected_identifiers= None
        self.result = None
        self.result_info = None
        self.main_view = main_view
        self.show_fields = "all"
        self.selected_items = None
        self.delete_btn = None
        self.result = None

        main_view.current_command_view = self

        types_menu_description = Label(main_view.main_area, borderwidth=2, relief="solid",
                                       text="Select OGC entity type (mandatory field)")
        self.view_elements.append({"item":types_menu_description, "row": 0, "column": 0})

        self.selected_type = StringVar(main_view.main_area)
        types = get_ogc_types()
        self.selected_type.set("Select an OGC type")

        self.selected_type.trace("w", self.show_options)

        types_menu = OptionMenu(main_view.main_area, self.selected_type, *types)
        self.view_elements.append({"item":types_menu, "row": 0, "column" : 1})

        selected_identifiers_description = Label(main_view.main_area, borderwidth=2, relief="solid",
                                                 text="Insert one or more names or @iot.id\n"
                                                                        "separated by a space\n"
                                                      "(by default all the items of selected type\n"
                                                      "will be selected)")

        self.view_elements.append({"item":selected_identifiers_description, "row": 1, "column" : 0})
        self.selected_identifiers = Entry(main_view.main_area, width=10)
        self.view_elements.append({"item": self.selected_identifiers, "row": 1, "column" : 1})

        selected_boolean_expression_description = Label(main_view.main_area, borderwidth=2, relief="solid",
                                                        text="Insert a filter for results\n "
                                                                               "(<,>,==,in,not in)(and or not)")
        self.view_elements.append({"item":selected_boolean_expression_description, "row": 2, "column" : 0})
        self.selected_boolean_expression = Entry(main_view.main_area, width=50)
        self.view_elements.append({"item":self.selected_boolean_expression, "row": 2, "column" : 1})

        fields_menu_description = Label(main_view.main_area, borderwidth=2, relief="solid",
                                        text="Select fields to show (default: all)")
        self.view_elements.append({"item":fields_menu_description, "row": 3, "column": 0})

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
        self.view_elements.append({"item": self.show_fields, "row": 4, "column": 0, "name": "show_fields"})

        search_btn = Button(self.main_view.main_area, text="Search!", command=lambda: search(self),
                            bg = "#86f986")
        self.view_elements.append({"item": search_btn, "row": 5, "column": 1})

        populate(self.view_elements, self.main_view.main_area)


def get_command(view):
    view.back_button.grid()
    view.hide()
    GetView(view)


def search(self):
    clear_results(self)
    selected_items = get_items(self)
    if selected_items != "error":
        self.result = Text(self.main_view.main_area, width=50, height=10)
        row = 0
        for i in selected_items:
            formatted_record = json.dumps(i, sort_keys=True, indent=2) + "\n"
            self.result.insert(f"1.0", formatted_record)
            row += 1

        self.view_elements.append({"item": self.result, "row": 4, "column": 1, "name": "result"})

        self.result_info = Label(self.main_view.main_area, borderwidth=2, relief="solid",
                                       text=f"found {len(selected_items)} results")
        self.view_elements.append({"item": self.result_info, "row": 3, "column": 1})
        populate(self.view_elements, self.main_view.main_area)
