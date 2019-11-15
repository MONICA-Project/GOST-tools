import requests
import connection_config
import evaluator_package.evaluating_conditions_decorator as eval_cond


def get_item_by_name(ogc_name, environment, name, sending_address):
    result = []
    if environment:
        GOST_address = environment["GOST_address"]
        sending_address = GOST_address + "/" + ogc_name +"?$filter=name eq " + name
    elif not sending_address:
        GOST_address = connection_config.get_address_from_file()
        sending_address = GOST_address + "/" + ogc_name +"?$filter=name eq " + name

    r = requests.get(sending_address)
    response = r.json()
    if "value" in response:
        result = response["value"]
    elif isinstance(response, dict) and "value" not in response:  # condition for when the response is a single item
        if any(response):
            result.append(response)
    return result


def item_is_already_present(name, type):
    """check if an item with given name is already present"""
    if eval_cond.get(ogc_type=type, ogc_name=name):
        return "Item with name " + name + " is already present"
    else:
        return False


def error_exists(checkResult):
    """check if in conditions array exists at least one non-False value (an error)
    """
    for value in checkResult:
        if value:
            return True
    return False


def sensor_is_already_present(name):
    """Check if a sensor with given name is already present"""
    return item_is_already_present(name, 'Sensors')


def thing_is_already_present(name):
    """Check if a thing with given name is already present"""
    return item_is_already_present(name, 'Things')


def observed_property_is_already_present(name):
    """Check if a observed property with given name is already present"""
    return item_is_already_present(name, 'ObservedProperties')


def data_stream_is_already_present(name):
    """Check if a data stream with given name is already present"""
    return item_is_already_present(name, 'Datastreams')


def feature_of_interest_is_already_present(name):
    """ Finds if the feature of interest with name "name" is already present.
    """
    return item_is_already_present(name, 'FeaturesOfInterest')


def field_is_void(field):
    """Check if the field in the parameter is void, otherwise return False"""
    if field == '':
        return "Field not available"
    else:
        return False


def location_is_already_present(name):
    """ Finds if the location with name "name" is already present.
    """
    return item_is_already_present(name, 'Locations')