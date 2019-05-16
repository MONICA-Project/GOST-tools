import json
from checking_functions import item_is_already_present
import random
import string


def create_records_file(args, ogc_type):
    """create records in default file or in a specified file, if provided"""
    result = {"created_name_list" : [],"errors" : []}
    if "file" in args:
        file_name = args["file"]
    else:
        file_name = "created_files/" + ogc_type

    my_file = open(file_name, "w")

    for x in range(int(args["num"])):
        item = create_random_item(args, ogc_type)
        if "error" in item:
            result["errors"].append(item["error"])
        else:
            my_file.write(item)
            result["created_name_list"].append(json.loads(item))

    my_file.close()
    print("Created a file in " + file_name
          + " with " + str(len(result["created_name_list"])) + " " + ogc_type)
    return result


def create_random_item(args, ogc_type):
    if ogc_type == "Sensors":
        return create_random_sensor(args)
    if ogc_type == "Observations":
        return create_random_observation(args)
    if ogc_type == "Things":
        return create_random_thing(args)
    if ogc_type == "Locations":
        return create_random_location(args)
    else:
        return {"error": "incorrect ogc type"}


def create_random_sensor(args):
    return json.dumps({
        "name": user_defined_or_default(args, "name", "Sensors"),
        "description": user_defined_or_default(args, "description"),
        "encodingType": "application/pdf",
        "metadata": user_defined_or_default(args, "metadata")
        }) + "\n"


def create_random_thing(args):
    return json.dumps({
        "name": user_defined_or_default(args, "name", "Things"),
        "description": user_defined_or_default(args, "description"),
        "properties": {
        "organisation": user_defined_or_default(args, "organisation"),
        "owner": user_defined_or_default(args, "owner")
        }
}) + "\n"


def create_random_observation(args):
    if "Datastream" not in args:
        return {"error": "missing datastream"}
    return json.dumps({
        "result": user_defined_or_default(args, "result"),
        "Datastream": {
        "@iot.id": args["datastream"]},
        "FeatureOfInterest" : {"@iot.id": args["feature_of_interest"]}}) + "\n"

def create_random_location(args):
    return json.dumps({
    "name": user_defined_or_default(args, "name", "Locations"),
    "description": user_defined_or_default(args, "description"),
    "encodingType": user_defined_or_default(args, "encodingType", "Locations"),
    "location": {
        "coordinates":
            user_defined_or_default(args, "coordinates")
        ,
        "type": user_defined_or_default(args, "type")}}) + "\n"


def random_string(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def valid_random_name(ogc_type):
    name = random_string()
    while item_is_already_present(name, ogc_type):
        name = random_string()
    return name


def user_defined_or_default(args, field_name, ogc_type=None):
    if field_name in args:  # using user-defined value for the field
        result = None
        if field_name == "coordinates" and bool(args["coordinates"]):
            result = string_to_coordinates(args["coordinates"])
        else:
            result = args[field_name]
        return result

    elif field_name == "name":
        return valid_random_name(ogc_type)
    elif field_name == "encodingType" and ogc_type == "Locations":
        return "application/vnd.geo+json"
    else:
        return "default " + field_name


def string_to_coordinates(string):
    result = string.split(",")
    for i in result:
        i = float(i)
    return result
