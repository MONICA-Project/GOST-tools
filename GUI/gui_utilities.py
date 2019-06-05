from checking_functions import *
from tkinter import *
from ogc_utility import *
from evaluator_package import selection_parser
import copy


def populate(elements_list):
    for i in elements_list:
        i["item"].grid(column=i["column"], row=i["row"])


def restore(self):
    populate(self.main_view_elements)


def clear_results(self):
    indexes_to_delete = []
    if bool(self.result):
        self.result.grid_forget()
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["result"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        del self.view_elements[i]


def get_items(self):
    selected_items = []
    if self.selected_type.get() == "Select an OGC type":
        result = Text(self.main_view.window, width=50, height=1)
        result.insert("1.0", "Error: OGC type needed")
        result.grid(column=0, row=9)
        self.view_elements.append({"item": result, "row": 9, "column": 0})
        return "error"
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
        return selected_items
