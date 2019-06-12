import json
from checking_functions import item_is_already_present
import random


def create_records(values, number, ogc_type=False):
    """create a list of records with selected values or default for specified ogc type

    :param values:the created item's field value
    :param values:number of items to create
    :param ogc_type: the entity type of the created records
    :return: a dictionary whit two lists, one of the created items and the other of the eventual errors
    """
    result = {"created_items" : [],"errors" : []}

    for x in range(number):
        item = create_random_item(values, ogc_type)
        if "error" in item:
            result["errors"].append(item["error"])
            break
        else:
            result["created_items"].append(json.loads(item))
    return result


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
    arguments given by the user, or the default value.
    The type can be provided as argument or as 'type' key of args

    :param args: user provided values for the new item field
    :param ogc_type: entity type of the created item
    :return: a string representation of the created item
    """
    if not ogc_type:
        ogc_type = args["type"]

    if "name" in args:  # checking for duplicate names
        if item_is_already_present(args["name"], ogc_type):
            return {"error": f"name 'f{args['name']}' already present in {ogc_type}"}

    if ogc_type == "Sensors":
        return json.dumps({
            "name": user_defined_or_default(args, "name", "Sensors"),
            "description": user_defined_or_default(args, "description"),
            "encodingType": "application/pdf",
            "metadata": user_defined_or_default(args, "metadata")
        }) + "\n"

    if ogc_type == "Observations":
        missing_fields = needed_user_defined_fields(args, ["Datastream_id"])
        if bool(missing_fields):
            return missing_fields
        return json.dumps({
            "result": user_defined_or_default(args, "result"),
            "Datastream": {"@iot.id": args["Datastream_id"]},
            "FeatureOfInterest": user_defined_or_default(args, "FeatureOfInterest")
            }) + "\n"

    if ogc_type == "Things":
        return json.dumps({
            "name": user_defined_or_default(args, "name", "Things"),
            "description": user_defined_or_default(args, "description"),
            "properties": {"organization": user_defined_or_default(args, "organization"),
                           "owner": user_defined_or_default(args, "owner")},
        }) + "\n"

    if ogc_type == "Locations":
        return json.dumps({"name": user_defined_or_default(args, "name", "Locations"),
                           "description": user_defined_or_default(args, "description"),
                           "encodingType": user_defined_or_default(args, "encodingType", "Locations"),
                           "Location": {"coordinates": user_defined_or_default(args, "coordinates"),
                                        "type": user_defined_or_default(args, "type")}}) + "\n"

    if ogc_type == "ObservedProperties":
        missing_fields = needed_user_defined_fields(args, ["Definition", "Description"])
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
                                "@iot.id": user_defined_or_default(args, "Sensor_id", "Datastreams"),}}) + "\n"

    if ogc_type == "FeaturesOfInterest":
        return json.dumps({"name": user_defined_or_default(args, "name"),
                "description": user_defined_or_default(args, "description"),
                "encodingType": user_defined_or_default(args, "encodingType"),
                "feature": user_defined_or_default(args, "feature")}) + "\n"


    else:
        return {"error": "incorrect ogc type"}


def needed_user_defined_fields(args, fields_list):
    """Verifies if the list of needed fields has been provided by the user

    :param args: user provided arguments
    :param fields_list: needed fields name
    :return: if missing, a list of the missing fields names
    """
    result = {}
    args_keys_names = []
    for i in args:
        args_keys_names.append(i.title())
    for field in fields_list:
        if field not in args_keys_names:
            if "error" in result:
                result["error"] = result["error"] + f", {field} value"
            else:
                result["error"] = f"missing {field} value"
    return result


def random_name_generator(range, ogc_type):
    """creates a random name for the new record, composed by a number of <range> figures,
    followed by '_<ogc_type>' """
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

    if ("type" in args) and not bool(ogc_type):
        ogc_type = args["type"]
    if field_name in args:  # using user-defined value for the field
        if field_name == "coordinates":
            result = string_to_coordinates(args["coordinates"])
        else:
            result = args[field_name]
        return result

    #  default values, if not provided by user, for special fields
    elif field_name == "name":
        return valid_random_name(ogc_type)

    elif field_name == "feature":
        return {"coordinates": [4.9132, 52.34227],"type": "Point"}

    elif field_name == "FeatureOfInterest":
        if args["FeatureOfInterest_id"]:
            return {"@iot.id": args["FeatureOfInterest_id"]}
        else:
            return ""

    elif field_name == "observationType":
        return "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"

    elif field_name == "encodingType":
        return "application/vnd.geo+json"

    elif field_name == "coordinates":
        return [4.9132, 52.34227]

    elif field_name == "type":
        return "Point"

    else:
        return "default " + field_name


def string_to_coordinates(coordinate_string):
    """Converts a string representing coordinates to a list of coordinates"""
    result = coordinate_string.split(",")
    for i in result:
        i = float(i)
    return result
