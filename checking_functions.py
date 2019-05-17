import requests
import connection_config


def get_all(ogc_name, environment = None):
    """sends a GET request for the list of all OGC items of ogcName type
    Returns an array of Ogc items in form of a dictionary
    """
    if environment:
        GOST_address = environment["GOST_address"]
    else:
        GOST_address = connection_config.get_address_from_file()
    sending_address = GOST_address + "/" + ogc_name
    r = requests.get(sending_address)
    return r.json()["value"]


def item_is_already_present(name, type):
    """check if an item with given name is already present"""
    for x in get_all(type):
        if x["name"] == name:
            return "Item with name " + name + " is already present"
    return False


def error_exists(checkResult):
    """check if in conditions array exists at least one non-False value (an error)
    """
    for value in checkResult:
        if value:
            return True
    return False


def sensor_is_already_present(name):
    return item_is_already_present(name, 'Sensors')


def thing_is_already_present(name):
    return item_is_already_present(name, 'Things')


def observed_property_is_already_present(name):
    return item_is_already_present(name, 'ObservedProperties')


def data_stream_is_already_present(name):
    return item_is_already_present(name, 'Datastreams')


def feature_of_interest_is_already_present(name):
    """ Finds if the feature of interest with name "name" is already present.
    """
    return item_is_already_present(name, 'FeaturesOfInterest')


def field_is_void(field):
    if field == '':
        return "Field not available"
    else:
        return False


def location_is_already_present(name):
    """ Finds if the feature of interest with name "name" is already present.
    """
    return item_is_already_present(name, 'Locations')