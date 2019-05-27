import json
from checking_functions import item_is_already_present
import random


def create_records_file(args, ogc_type=False):
    """create records in default file or in a specified file, if provided

    :param args:the command line args provided for "create" command
    :param ogc_type: the entity type of the created records
    :return: a list of the created items and a list of the eventual errors
    """
    if not ogc_type:
        ogc_type = args["type"]
    result = {"created_name_list" : [],"errors" : []}
    if "file" in args:
        file_name = args["file"]
    else:
        file_name = "created_files/" + ogc_type

    my_file = open(file_name, "w")
    number_of_items = 0

    for x in range(int(args["num"])):
        item = create_random_item(args, ogc_type)
        if "error" in item:
            result["errors"].append(item["error"])
            break
        else:
            my_file.write(item)
            number_of_items += 1

    my_file.close()
    if number_of_items > 0:
        print("Created a file in " + file_name
              + " with " + str(number_of_items) + " " + ogc_type)
    return result


def create_random_item(args, ogc_type=False):
    """Creates a random item of given type, with fields filled with the
    arguments given by the user"""
    if not ogc_type:
        ogc_type = args["type"]

    if ogc_type == "Sensors":
        return json.dumps({
            "name": user_defined_or_default(args, "name", "Sensors"),
            "description": user_defined_or_default(args, "description"),
            "encodingType": "application/pdf",
            "metadata": user_defined_or_default(args, "metadata")
        }) + "\n"

    if ogc_type == "Observations":
        missing_fields = needed_user_defined_fields(args, ["Datastream"])
        if bool(missing_fields):
            return missing_fields
        return json.dumps({
            "result": user_defined_or_default(args, "result"),
            "Datastream": {"@iot.id": args["datastream"]},
            "FeatureOfInterest": {"@iot.id": args["feature_of_interest"]}}) + "\n"

    if ogc_type == "Things":
        return json.dumps({
            "name": user_defined_or_default(args, "name", "Things"),
            "description": user_defined_or_default(args, "description"),
            "properties": {"organisation": user_defined_or_default(args, "organisation"),
                           "owner": user_defined_or_default(args, "owner")}}) + "\n"

    if ogc_type == "Locations":
        missing_fields = needed_user_defined_fields(args, ["Location"])
        if bool(missing_fields):
            return missing_fields
        return json.dumps({"name": user_defined_or_default(args, "name", "Locations"),
                           "description": user_defined_or_default(args, "description"),
                           "encodingType": user_defined_or_default(args, "encodingType", "Locations"),
                           "location": {"coordinates": user_defined_or_default(args, "coordinates"),
                                        "type": user_defined_or_default(args, "type")}}) + "\n"

    if ogc_type == "ObservedProperties":
        missing_fields = needed_user_defined_fields(args, ["Definition"])
        if bool(missing_fields):
            return missing_fields
        return json.dumps({"name": user_defined_or_default(args, "name", "ObservedProperties"), "description":
                          user_defined_or_default(args, "description", "ObservedProperties"), "definition":
                          user_defined_or_default(args, "definition", "ObservedProperties")}) + "\n"

    if ogc_type == "Datastreams":
        missing_fields = needed_user_defined_fields(args, ["Thing_id", "ObservedProperty_id", "Sensor_id"])
        if bool(missing_fields):
            return missing_fields
        return json.dumps({"name": user_defined_or_default(args, "name", "Datastreams"),
                           "description": user_defined_or_default(args, "description", "Datastreams"),
                           "observationType": user_defined_or_default(args, "observationType", "Datastreams"),
                           "unitOfMeasurement": {
                                "definition": user_defined_or_default(args, "unitOfMeasurement_definition",
                                                                      "Datastreams"),
                                "name": user_defined_or_default(args, "unitOfMeasurement_name",
                                                                "Datastreams"),
                                "symbol": user_defined_or_default(args, "unitOfMeasurement_symbol",
                                                                  "Datastreams")},
                           "Thing": {
                                "@iot.id": user_defined_or_default(args, "Thing_id", "Datastreams"),},
                            "ObservedProperty": {
                                "@iot.id": user_defined_or_default(args, "ObservedProperty_id", "Datastreams"),
                            },
                            "Sensor": {
                                "@iot.id": user_defined_or_default(args, "Sensor_id", "Datastreams"),
    }
}
) + "\n"

    else:
        return {"error": "incorrect ogc type"}

def needed_user_defined_fields(args, fields_list):
    result = {}
    for field in fields_list:
        if field not in args:
            if "error" in result:
                result["error"] = result["error"] + f"\nmissing {field} value"
            else:
                result["error"] = f"missing {field} value"
    return result

def random_name_generator(range, ogc_type):
    """creates a random name for the new record, composed by a number <= 10^range,
    padded on the left with zeroes if shorter than range"""
    numerical_name_side = str(random.randint(0, 10**range)).zfill(range)
    return numerical_name_side + "_" + ogc_type


def valid_random_name(ogc_type):
    """given an ogc type, checks and returns a valid random name for a new item
    of that type"""
    name = random_name_generator(5, ogc_type)
    while item_is_already_present(name, ogc_type):
        name = random_name_generator(5, ogc_type)
    return name


def user_defined_or_default(args, field_name, ogc_type=None):
    """Given a field name, returns its default value or the user-defined
    one if present"""
    if field_name in args:  # using user-defined value for the field
        if (field_name == "coordinates") and (bool(args["coordinates"])):
            result = string_to_coordinates(args["coordinates"])
        else:
            result = args[field_name]
        return result

    elif field_name == "name":
        return valid_random_name(ogc_type)

    elif field_name == "observationType":
        return "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"

    elif field_name == "encodingType" and ogc_type == "Locations":
        return "application/vnd.geo+json"

    else:
        return "default " + field_name


def string_to_coordinates(coordinate_string):
    result = coordinate_string.split(",")
    for i in result:
        i = float(i)
    return result
