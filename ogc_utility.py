from flask import jsonify, make_response, Flask
from condition_manager import *
from condition_config import *
import connection_config
import json
import shlex


def get_id_list(dict_list):
    """returns a list of all IDs of the items in a list of dictionaries

    :param dict_list: a list of entities in form of dictionaries
    :return: a list of all the entities id's
    """
    values_array = []
    items_array = dict_list.get('value')
    for x in items_array:
        values_array.append(x.get('@iot.id'))

    return values_array


def send_json(provided_load=None, ogc_name=None, sending_address=None, request_type='POST'):
    """ sends a http request with provided load and type = request_type


    :param provided_load: the load to send, accepts both dictionaries or strings
    :param ogc_name: the ogc name of the entity, used if no sending_address is provided
    :param sending_address: the address to which to send the request
    :param request_type: the type of the request, default is POST
    :return:
    """
    if not sending_address:
        sending_address = connection_config.get_address_from_file() + "/" + ogc_name
    if provided_load:
        if isinstance(provided_load, str):
            load = json.dumps(provided_load)
        else:
            load = provided_load
    else:
        load = ""
    headers = {'Content-type': 'application/json'}
    if request_type == 'POST':
        r = requests.post(sending_address, json=load, headers=headers)
    if request_type == 'PATCH':
        r = requests.patch(sending_address, json=load, headers=headers)
    if request_type == 'GET':
        r = requests.get(sending_address, data=load, headers=headers)
    return r


def get_item_id_by_name(name, type, environment = None):
    """finds the id of the item of type "type" with a given name

    :param name: name or id of the item
    :param type: entity type of the item to get
    :param environment: the current environment
    :return: the item id
    """
    json_response = get_all(type, environment)
    for x in json_response:
        if x.get("name") == name:
            return x["@iot.id"]
    return False


def get_item(identifier, ogc_type, environment=None, address=False):
    """finds the id of the item of type "type" with a given name or id
    """
    if not identifier.isdigit():
        identifier = get_item_id_by_name(identifier, ogc_type, environment)
    if not address:
        address = environment["GOST_address"] + "/"
    query_address = f"{address}{ogc_type}({identifier})"
    response = send_json("", sending_address=query_address, request_type= "GET")
    json_response = response.json()
    if "error" in json_response:
        json_response["error"]["message"].append("item id: " + str(identifier))
    return json_response


def add_item(req, type, spec = None):
    """add an item from request "req" of type "type" with specs "spec"
    """

    app = Flask(__name__)
    with app.app_context():
        if isinstance(req, dict):
            content = req
        else:
            content = req.get_json()

        if not bool(spec):
            spec = get_specs(type)

        conditions_results = checkConditions(spec, content)

        if error_exists(conditions_results):
            return make_response(jsonify(error="missing conditions " + str(conditions_results)), 400)
        else:
            s = send_json(content, type)
            if s:
                if type != 'Observations':
                    return make_response(
                        jsonify(success=("added to " + type),
                                id=str(get_item_id_by_name(content.get('name'), type))),
                        201)
                else:
                    return make_response(jsonify(success=("added to " + type)), 201)
            else:
                return make_response(jsonify(error=("not added to " + type + " "
                                                    + (json.loads(s.text))["error"]["message"][0])), 500)


def patch_item(options_dict, identifier, ogc_type, environment):
    """patch the item identified by 'identifier' with the fields
    provided with 'options_dict'
    """
    GOST_address = environment["GOST_address"] + "/"
    address = f"{GOST_address}{ogc_type}({check_id(identifier)})"
    if "name" in options_dict:
        if item_is_already_present(options_dict["name"], ogc_type):
            return {"error" : f"Trying to patch "
            f"with name {options_dict['name']} already present in {ogc_type}"}

    return send_json(provided_load=options_dict, sending_address=address, request_type='PATCH').json()


def check_id(item_identifier):
    """get the id of the item identified by item_identifier, which can be a name or an id

    :param item_identifier: the name or id of an item
    :return: the item identifier if the item exists, an error otherwise
    """
    if not item_identifier.isnumeric():
        item_identifier = get_item_id_by_name(item_identifier, type)
    if not item_identifier:
        return "item not found"
    return item_identifier


def delete_by_id(id, ogcName, environment):
    """delete the item of type ogcName with id==n
    """
    address = environment["GOST_address"] + "/"
    r = requests.delete(f"{address}{ogcName}({str(id)})")
    return r


def delete_item(item_identifier, type, environment):
    """delete a single item

    :param item_identifier: the id of the item to delete
    :param type: the entity type of the item to delete
    :param environment: the current evaluating environment
    :return: returns a message of success or error as a dictionary
    """
    check_id(str(item_identifier))
    return_value = delete_by_id(str(item_identifier), type, environment)
    if return_value.ok:
        return {"success": f"deleted from {type}, identifier {item_identifier}"}
    else:
        return {"error": "delete failed"}


def delete_all(entity_name, environment):
    """delete all the items of a single entity type

    :param entity_name: the name of the entity type to delete
    :param environment: the current evaluation environment
    :return: the current environment
    """
    all_list = get_id_list(get_all(entity_name, environment).json())
    for x in all_list:
        environment.selected_item.append(delete_by_id(x, entity_name, environment))
    return environment


def args_to_dict(args):
    """converts an array of strings [val_0, val_1,..., val_n]
    to a dictionary {val_0 : val_1,..., val_m - 1: val_m]

    :param args: the array to convert
    :return: the dictionary conversion
    """
    new_args = args
    while (len(new_args) % 2) != 0:
        new_args = shlex.split(input(f"This command requires an even number of arguments:\n"
                                     f"<argument 1> <value 1> <argument 2> <value 2> ... <argument n> <value n>\n"
                                     f"You provided {str(new_args)}\n"
                                     f"Insert valid args string\n"))
    i = iter(new_args)
    dict_result = dict(zip(i, i))
    return dict_result
