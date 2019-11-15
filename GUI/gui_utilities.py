import shlex
import json
import evaluator_package.evaluator as eval
import evaluator_package.evaluating_conditions_decorator as eval_cond
from tkinter import *
import ogc_utility as ogc_ut
import evaluator_package.default_functions as def_func
import copy
from tkinter import messagebox

# color names for interface


confirm_color = '#ff502f'
abort_color = '#86f986'
change_address_color = "#a7cce7"
action_color = "#86f986"

# common text fields

select_id_text = "Insert the name(s) or the @iot.id(s)\n separated by a space"

# "If no identifier is provided, all the records of the chosen OGC type will be selected"

select_conditions_text = "Insert a filter for results\n(<,>,==,in,not in)(and or not)"


def populate(elements_list, scrollable_area=False):
    for i in elements_list:
        i["item"].grid(column=i["column"], row=i["row"], sticky=N + S + E + W)
    if scrollable_area:
        scrollable_area.update()


def reset_attribute(item, attributes_list):
    for i in attributes_list:
        if i in item.__dict__:
            if isinstance(item.__dict__[i], list):
                item.__dict__[i] = []
            else:
                item.__dict__[i] = None


def restore(self):
    reset_attribute(self, ["selected_items", "selected_type", "selected_boolean_expression", "selected_identifiers",
                           "show_fields", "patch_values", "create_values", "create_entries", "created_items",
                           "storage_file"])
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


def list_reformat(items, split_type):
    items_list = items.split()
    return_list = []
    for item in items_list:
        if split_type in item:
            rearrange = item.split(split_type)
            for single_item in rearrange:
                return_list.append(single_item)
        else:
            return_list.append(item)
    return return_list


def get_items(self, b=False):
    selected_items = []
    error_message = ""
    if self.selected_type.get() == "Select an OGC type":
        result = Text(self.main_view.window, width=50, height=1)
        result.insert("1.0", "Error: OGC type needed")
        result.grid(column=0, row=9)
        self.view_elements.append({"item": result, "row": 9, "column": 1, "name": "result"})
        return "error"
    else:
        if bool(self.selected_identifiers.get()):
            identifiers = shlex.split(self.selected_identifiers.get())
            for i in identifiers:
                address = self.main_view.model.GOST_address + "/"
                item = ogc_ut.get_item(i, self.selected_type.get(), address=address)
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
            selected_items = eval_cond.get(self.selected_type.get())

        if bool(self.selected_boolean_expression.get()) and bool(self.selected_type.get()):  # filtering the results
            query = self.selected_boolean_expression.get().split()
            selected_items = eval_cond.get(ogc_type=self.selected_type.get(), select_query=query)
        if b:
            if self.related_type.get() != "No related OGC type" and bool(self.selected_type.get()):
                partial_items = []
                partial_items += related_elements(self, selected_items)
                selected_items = partial_items
        if bool(self.show_fields):

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


def related_elements(self, items):
    result = []
    error_message = "Error: trying to found Datastreams related to Datastreams"
    if self.selected_type.get() == "Datastreams":
        if self.related_type.get() == "Datastreams":
            return error_message
        else:
            if items:
                for i in items:
                    result += def_func.get_entities_from_datastream(i, self.related_type.get(),
                                                                    self.main_view.model.GOST_address)
    else:
        if self.related_type.get() == "Datastreams":
            for i in items:
                result += def_func.related_datastreams(i['@iot.id'], self.selected_type.get(),
                                                       self.main_view.model.GOST_address)
        else:
            for i in items:
                result += def_func.find_related(i, self.selected_type.get(), self.related_type.get(),
                                                self.main_view.model.GOST_address)
    return result


def str_to_list(ogc_type, str_query, separator):
    list_query = str_query.split(separator)
    return eval_cond.get(ogc_type=ogc_type, select_query=list_query)


def get_fields_names(ogc_type, needed_for_editing=False):
    values = []
    if ogc_type == "Sensors":
        values = ["name", "description", "encodingType", "metadata"]
    elif ogc_type == "Things":
        values = ["name", "description", "properties"]

    elif ogc_type == "ObservedProperties":
        values = ["name", "definition", "description"]

    elif ogc_type == "Datastreams":
        values = ["name", "description", "observationType", "unitOfMeasurement", "observedArea",
                  "phenomenonTime", "resultTime"]
        if needed_for_editing:
            values += ["Thing_id", "ObservedProperty_id", "Sensor_id", "unitOfMeasurement_definition",
                       "unitOfMeasurement_name", "unitOfMeasurement_symbol"]
        else:
            values += ["unitOfMeasurement", "Thing", "Sensor", "ObservedProperty"]

    elif ogc_type == "Observations":
        values = ["result", "FeatureOfInterest", "phenomenonTime", "resultTime", "resultQuality",
                  "validTime", "parameters"]
        if needed_for_editing:
            values += ["Datastream_id"]
        else:
            values += ["Datastream"]

    elif ogc_type == "FeaturesOfInterest":
        values = ["name", "description", "encodingType", "feature"]

    elif ogc_type == "Locations":
        values = ["name", "description", "encodingType"]
        if needed_for_editing:
            values += ["type", "coordinates"]
        else:
            values += ["Location"]

    return values


def get_ogc_types(b=None):
    if b:
        return {"Sensors", "Things", "Datastreams", "Locations", "ObservedProperties", "Observations",
                "FeaturesOfInterest", "No related OGC type"}
    else:
        return {"Sensors", "Things", "Datastreams", "Locations", "ObservedProperties", "Observations",
                "FeaturesOfInterest", }


def scrollable_results(results_list, root, editable=True):
    """Returns a scrollable view of results_list. If editable is false, the text will be read only"""
    txt_frm = Frame(root, width=600, height=300)
    # ensure a consistent GUI size
    txt_frm.grid_propagate(False)
    # implement stretchability
    txt_frm.grid_rowconfigure(0, weight=1)
    txt_frm.grid_columnconfigure(0, weight=1)

    # create a Text widget
    text_result = Text(txt_frm, width=50, height=10)
    text_result.config(font=("consolas", 8), undo=True, wrap='word')
    text_result.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    row = 0
    for i in results_list:
        formatted_record = json.dumps(i, sort_keys=True, indent=2) + "\n"
        text_result.insert(f"1.0", formatted_record)
        row += 1
    if not editable:
        text_result.config(state="disabled")

    # create a Scrollbar and associate it with txt
    scrollb = Scrollbar(txt_frm, command=text_result.yview)
    scrollb.grid(row=0, column=1, sticky='nsew')
    text_result['yscrollcommand'] = scrollb.set
    return txt_frm


def check_duplicates(list):
    """Checks for records with duplicate name in list"""

    names_list = []
    for i in list:
        if "name" in i:  # necessary for nameless entities like Observations
            names_list.append(i["name"])
    duplicate_dict = {}
    for j in names_list:
        if j in duplicate_dict:
            return False
        else:
            duplicate_dict[j] = True
    return list


def name_in_patch(patch_values):
    for i in patch_values:
        if i["field_name"] == "name":
            if bool(i["field_entry"].get()):
                return True
            else:
                return False
    return False
