from checking_functions import *
from tkinter import *
from ogc_utility import *
from evaluator_package import selection_parser
import copy
from tkinter import messagebox


def populate(elements_list, scrollable_area = False):
    for i in elements_list:
        i["item"].grid(column=i["column"], row=i["row"], sticky=E+W)
    if scrollable_area:
        scrollable_area.update()


def restore(self):
    populate(self.main_view_elements, self.main_view.main_area)


def clear_results(self):
    indexes_to_delete = []
    if bool(self.result):
        self.result.grid_forget()
    for index, val in enumerate(self.view_elements):
        if "name" in val:
            if val["name"] in ["result"]:
                indexes_to_delete.append(index)
    for i in sorted(indexes_to_delete, reverse=True):
        self.view_elements[i]["item"].grid_forget()
        del self.view_elements[i]


def get_items(self):
    selected_items = []
    error_message = ""
    if self.selected_type.get() == "Select an OGC type":
        result = Text(self.main_view.window, width=50, height=1)
        result.insert("1.0", "Error: OGC type needed")
        result.grid(column=0, row=9)
        self.view_elements.append({"item": result, "row": 9, "column": 1, "name" : "result"})
        return "error"
    else:
        if bool(self.selected_identifiers.get()):
            identifiers = shlex.split(self.selected_identifiers.get())
            for i in identifiers:
                address = self.main_view.model.GOST_address + "/"
                item = get_item(i, self.selected_type.get(),address=address)
                if "error" in item:
                    if "message" in item["error"]:
                        for k in map(str, item["error"]["message"]):
                            error_message += k + " "
                        error_message += "\n"

                    else:
                        for k in map(str, item["error"]):
                            error_message += k + " "
                        error_message += "\n"
                else:
                    selected_items.append(item)

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
                error_message += f"\nNo items found with select statement conditions\n"

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
        if bool(error_message):
            messagebox.showinfo("ERROR", error_message)
        return selected_items


def get_fields_names(ogc_type, needed_for_editing = False):
    values = []
    if ogc_type == "Sensors":
        values = ["name", "description", "encodingType", "metadata"]
    elif ogc_type == "Things":
        values =["name", "description"]
        if needed_for_editing:
            values += ["organization", "owner"]
        else:
            values += ["properties"]

    elif ogc_type == "ObservedProperties":
        values = ["name", "definition", "description"]

    elif ogc_type == "Datastreams":
        values = ["name", "description", "observationType", "unitOfMeasurement", "observedArea",
                "phenomenonTime", "resultTime"]
        if needed_for_editing:
            values += ["Thing_id", "ObservedProperty_id", "Sensor_id", "unitOfMeasurement_definition",
                       "unitOfMeasurement_name",  "unitOfMeasurement_symbol"]
        else:
            values += [ "unitOfMeasurement", "Thing", "Sensor", "ObservedProperty"]

    elif ogc_type == "Observations":
        values = ["result", "FeatureOfInterest"]
        if needed_for_editing:
            values += ["Datastream_id"]
        else:
            values += ["Datastream", "resultTime", "resultQuality", "validTime", "parameters"]

    elif ogc_type == "FeaturesOfInterest":
        values = ["name", "description", "encodingType", "feature"]

    elif ogc_type == "Locations":
        values = ["name", "description", "encodingType"]
        if needed_for_editing:
            values += ["type", "coordinates"]
        else:
            values += ["Location"]

    return values


def get_ogc_types():
    return {"Sensors", "Things", "Datastreams", "Locations", "ObservedProperties", "Observations", "FeaturesOfInterest"}

