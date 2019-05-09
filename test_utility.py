import json
from checking_functions import item_is_already_present
import random
import string


def create_records_file(args):
    """create records in default file or in a specified file, if provided"""
    errors = []
    created_name_list = []
    if "file" in args:
        file_name = args["file"]
    else:
        file_name = "created_files/" + args["type"]

    my_file = open(file_name, "w")

    for x in range(int(args["num"])):
        item = create_random_item(args)
        if "error" in item:
            errors.append(item["error"])
        else:
            my_file.write(item)
            created_name_list.append(item)

    my_file.close()
    return [created_name_list, errors]


def create_random_item(args):
    if args["type"] == "Sensors":
        return create_random_sensor(args)
    if args["type"] == "Observations":
        return create_random_observation(args)


def create_random_sensor(args):
    return json.dumps({
        "name": user_defined_or_default(args, "name"),
        "description": user_defined_or_default(args, "description"),
        "encodingType": "application/pdf",
        "metadata": user_defined_or_default(args, "metadata")
        }) + "\n"


def create_random_observation(args):
    random_obs_value = random.randint(1,100)
    if "Datasream" not in args:
        return {"error": "missing datastream"}
    return json.dumps({
        "result": user_defined_or_default(args, "result"),
        "Datastream": {
        "@iot.id": args["datastream"]},
        "FeatureOfInterest" : {"@iot.id": args["feature_of_interest"]}}) + "\n"


def random_string(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def valid_random_name(type):
    name = random_string()
    while item_is_already_present(name, type):
        name = random_string()
    return name


def user_defined_or_default(args, field_name):
    if field_name in args:
        return args[field_name]
    elif field_name == "name":
        return valid_random_name(args["type"])
    elif field_name == "description":
        return "default description"
    elif field_name == "metadata":
        return "default metadata"
