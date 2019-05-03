from flask import jsonify, make_response, Flask
from condition_manager import *
from condition_config import *
import connection_config


def get_id_list(dict_list):
    """returns a list of all IDs of the items
    in dict_list, received as <GOST response>.json()
    """
    values_array = []
    items_array = dict_list.get('value')
    for x in items_array:
        values_array.append(x.get('@iot.id'))

    return values_array


def send_json(string_to_jsonify = None, ogc_name=None, sending_address=None, request_type='POST'):
    """ sends a POST request with json body, ogcName is the name in OGC data model
    """
    if not sending_address:
        sending_address = "http://" + connection_config.get_address_from_file() + "/v1.0/" + ogc_name
    if string_to_jsonify:
        if isinstance(string_to_jsonify, dict):
            load = string_to_jsonify
        else:
            load = json.dumps(string_to_jsonify)
    else:
        load = ""
    headers = {'Content-type': 'application/json'}
    if request_type == 'POST':
        r = requests.post(sending_address, json=load, headers=headers)
    if request_type == 'PATCH':
        r = requests.patch(sending_address, data=load, headers=headers)
    if request_type == 'GET':
        r = requests.get(sending_address, data=load, headers=headers)
    return r


def get_item_id_by_name(name, type, environment = None):
    """finds the id of the item of type "type" with a given name
    """
    json_response = get_all(type, environment)
    for x in json_response:
        if x.get("name") == name:
            return x["@iot.id"]
    return False


def get_item(identifier, ogc_type, environment):
    """finds the id of the item of type "type" with a given name or id
    """
    if not identifier.isdigit():
        identifier = get_item_id_by_name(identifier, ogc_type, environment)
    address = "http://" + environment["GOST_address"] + "/v1.0/"
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

        if not spec:
            spec = get_specs(type)

        conditions_results = checkConditions(spec, content)
        if errorExists(conditions_results):
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
    """add an item from request "req" of type "type" with specs "spec"
    """
    GOST_address = "http://" + environment["GOST_address"] + "/v1.0/"
    address = f"{GOST_address}{ogc_type}({check_id(identifier)})"
    send_json(options_dict, sending_address=address, request_type = 'PATCH')


def addDataStream(req, spec):
    content = req.get_json()
    conditionsResults = checkConditions(spec, content)

    if errorExists(conditionsResults):
        return make_response(jsonify(error="missing conditions " + str(conditionsResults)), 400)

    else:
        destinationAddress = f"{connection_config.GOST_address}Things({content.get('thingId')})/Datastreams"
        s = send_json(content, 'DataStreams', destinationAddress)

        if (s) :
            return make_response(jsonify(success="added datastream", id = str(get_item_id_by_name(content.get('name'), 'Datastreams'))), 201)

        else :
            return make_response(jsonify(error="not added to datastreams", brokerErrorMessage = s.json()), 400)


def check_id(item_identifier):
    if not item_identifier.isnumeric():
        item_identifier = get_item_id_by_name(item_identifier, type)
    if not item_identifier:
        return "item not found"
    return item_identifier


def delete_by_id(id, ogcName, environment):
    """delete the item of type ogcName with id==n
    """
    address = "http://" + environment["GOST_address"] + "/v1.0/"
    r = requests.delete(f"{address}{ogcName}({str(id)})")
    return r


def delete_item(item_identifier, type, environment):
    check_id(str(item_identifier))
    return_value = delete_by_id(str(item_identifier), type, environment)
    return return_value


def delete_all(ogc_name, environment):
    """delete all the items of type ogcName
    """
    all_list = get_id_list(get_all(ogc_name, environment).json())
    for x in all_list:
        environment.selected_item.append(delete_by_id(x, ogc_name, environment))
    return environment


def add_observation(req, client) :
    """add an observation to a topic"""
    content = req.get_json()
    datastream_id = content.get('Datastream').get('@iot.id')
    topic = "GOST/Datastreams("+str(datastream_id)+")/Observations"
    return client.publish(topic=topic, payload=str(content), qos=2)


def get_info(options_dict, ogc_name, identifier = None):
    if not identifier:
        found_item = (get_all(ogc_name).json())['value']
    else:
        found_item = [get_item(identifier, ogc_name)]
        return found_item
    result = []
    for item in found_item:
        result.append(all_matching_fields(item, options_dict))
    return result


def all_matching_fields(item, options_dict):
    for key in options_dict:
        if not(item[key] == options_dict[key]):
            return False
    return True


def args_to_dict(args):
    i = iter(args)
    dict_result = dict(zip(i, i))
    return dict_result
