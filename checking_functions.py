import requests
import connection_config
import urllib.parse as urlparse


def get_all(ogc_name=None, environment=None, payload=None, sending_address=False):
    """sends a GET request for the list of all OGC items of ogcName type
    Returns an array of Ogc items in form of a dictionary
    """
    result = []
    if environment:
        GOST_address = environment["GOST_address"]
        sending_address = GOST_address + "/" + ogc_name
    elif not sending_address:
        GOST_address = connection_config.get_address_from_file()
        sending_address = GOST_address + "/" + ogc_name

    r = requests.get(sending_address, payload)
    response = r.json()
    if "value" in response:
        result = response["value"]
    if "@iot.nextLink" in response:  # iteration for getting results beyond first page
        next_page_address = "http://" + response["@iot.nextLink"]
        parsed = urlparse.urlparse(next_page_address)
        params = urlparse.parse_qsl(parsed.query)
        new_payload = {}
        for x, y in params:
            new_payload[x] = y
        partial_result = get_all(payload=new_payload, sending_address=next_page_address)
        (result).extend(partial_result)

    return result


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