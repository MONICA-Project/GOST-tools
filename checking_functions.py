from flask import json
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
    sending_address = "http://" + GOST_address + "/v1.0/" + ogc_name
    r = requests.get(sending_address)
    return r.json()["value"]


def item_is_already_present(name, type):
    for x in get_all(type):
        if x["name"] == name:
            return "Item with name " + name + "is already present"
    return False


#check if in conditions array exists at least one non-False value (an error)
def errorExists(checkResult) :
    for value in checkResult:
        if value :
            return True
    return False

##############################################SPECS FUNCTIONS###########################################################

#finds if the sensor of type ogcName with name "name" is already present
def sensorIsAlreadyPresent(name):
    return item_is_already_present(name, 'Sensors')

#finds if the thing of type ogcName with name "name" is already present
def thingIsAlreadyPresent(name):
    return item_is_already_present(name, 'Things')

#finds if the observed property with name "name" is already present
def observedPropertyIsAlreadyPresent(name):
    return item_is_already_present(name, 'ObservedProperties')

#finds if the dataStream  with name "name" is already present
def dataStreamIsAlreadyPresent(name):
    return item_is_already_present(name, 'Datastreams')


def featureOfInterestIsAlreadyPresent(name):
    """ Finds if the feature of interest with name "name" is already present.
    """
    return item_is_already_present(name, 'FeaturesOfInterest')

#check  if the field is an empty string
def fieldIsVoid(description) :
    if (description == ''):
        return "Field not available"
    else :
        return False


def locationIsAlreadyPresent(name):
    """ Finds if the feature of interest with name "name" is already present.
    """
    return item_is_already_present(name, 'Locations')