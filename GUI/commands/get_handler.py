import GUI.gui_utilities as gui_ut


class GetView:
    def __init__(self, main_view):
        self.view_elements = []
        self.selected_type = None
        self.selected_boolean_expression = None
        self.selected_identifiers = None
        self.result = None
        self.result_info = None
        self.main_view = main_view
        self.show_fields = "all"
        self.selected_items = None
        self.delete_btn = None
        self.result = None

        main_view.current_command_view = self

        types_menu_description = gui_ut.Label(main_view.main_area, borderwidth=2, relief="solid",
                                              text="Select OGC entity type (mandatory field)")
        self.view_elements.append({"item": types_menu_description, "row": 0, "column": 0})

        self.selected_type = gui_ut.StringVar(main_view.main_area)
        types = gui_ut.get_ogc_types()
        self.selected_type.set("Select an OGC type")

        self.selected_type.trace("w", self.show_options)

        types_menu = gui_ut.OptionMenu(main_view.main_area, self.selected_type, *types)
        self.view_elements.append({"item": types_menu, "row": 0, "column": 1})

        selected_identifiers_description = gui_ut.Label(main_view.main_area, borderwidth=2, relief="solid",
                                                        text=gui_ut.select_id_text)

        self.view_elements.append({"item": selected_identifiers_description, "row": 1, "column": 0})
        self.selected_identifiers = gui_ut.Entry(main_view.main_area, width=10)
        self.view_elements.append({"item": self.selected_identifiers, "row": 1, "column": 1})

        selected_boolean_expression_description = gui_ut.Label(main_view.main_area, borderwidth=2, relief="solid",
                                                               text=gui_ut.select_conditions_text)

        self.view_elements.append({"item": selected_boolean_expression_description, "row": 2, "column": 0})
        self.selected_boolean_expression = gui_ut.Entry(main_view.main_area, width=50)
        self.view_elements.append({"item": self.selected_boolean_expression, "row": 2, "column": 1})

        types_menu_description = gui_ut.Label(main_view.main_area, borderwidth=2, relief="solid",
                                              text="Select Related OGC entity type (optional field)")
        self.view_elements.append({"item": types_menu_description, "row": 3, "column": 0})

        self.related_type = gui_ut.StringVar(main_view.main_area)
        types = gui_ut.get_ogc_types(True)
        self.related_type.set("No related OGC type")

        self.related_type.trace("w", self.show_options)

        types_menu = gui_ut.OptionMenu(main_view.main_area, self.related_type, *types)
        self.view_elements.append({"item": types_menu, "row": 3, "column": 1})

        fields_menu_description = gui_ut.Label(main_view.main_area, borderwidth=2, relief="solid",
                                               text="Select fields to show (default: all)")
        self.view_elements.append({"item": fields_menu_description, "row": 4, "column": 0})

        gui_ut.populate(self.view_elements, self.main_view.main_area)

    def hide(self):
        for i in self.view_elements:
            i["item"].grid_forget()

    def show_options(self, a, b, c):  # additional parameters a b c needed because it is called by Trace function
        gui_ut.clear_results(self)

        if self.related_type.get() != "No related OGC type":
            field_names = gui_ut.get_fields_names(self.related_type.get())
        elif self.related_type.get() == "No related OGC type":
            field_names = gui_ut.get_fields_names(self.selected_type.get())

        self.show_fields = gui_ut.Listbox(self.main_view.main_area, selectmode=gui_ut.MULTIPLE)

        self.show_fields.insert(gui_ut.END, "@iot.id")

        for item in field_names:
            self.show_fields.insert(gui_ut.END, item)

        self.show_fields.grid(column=1, row=8)
        self.view_elements.append({"item": self.show_fields, "row": 5, "column": 0, "name": "show_fields"})

        search_btn = gui_ut.Button(self.main_view.main_area, text="Search!", command=lambda: search(self),
                                   bg=gui_ut.action_color)
        self.view_elements.append({"item": search_btn, "row": 6, "column": 1})

        gui_ut.populate(self.view_elements, self.main_view.main_area)


def get_command(view):
    view.back_button.grid()
    view.hide()
    GetView(view)


def search(self):
    gui_ut.clear_results(self)
    b = True
    selected_items = gui_ut.get_items(self, b)
    if selected_items != "error":
        self.result = gui_ut.scrollable_results(selected_items, self.main_view.main_area)

        self.view_elements.append({"item": self.result, "row": 5, "column": 1, "name": "result"})

        self.result_info = gui_ut.Label(self.main_view.main_area, borderwidth=2, relief="solid",
                                        text=f"found {len(selected_items)} results")
        self.view_elements.append({"item": self.result_info, "row": 4, "column": 1})
        gui_ut.populate(self.view_elements, self.main_view.main_area)
