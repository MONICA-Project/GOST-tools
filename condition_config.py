from checking_functions import *

sensorSpecs = {"name": sensorIsAlreadyPresent, "description": fieldIsVoid}
thingSpecs = {"name": thingIsAlreadyPresent}
observedPropertySpecs = {"name": observedPropertyIsAlreadyPresent}
dataStreamSpecs = {"name": dataStreamIsAlreadyPresent}
observationSpecs = {}
locationSpecs = {"name": locationIsAlreadyPresent}
featureOfInterestSpecs = {"name": featureOfInterestIsAlreadyPresent}


def get_specs(ogc_name):
    if ogc_name == "Sensors":
        return sensorSpecs
    if ogc_name == "Locations":
        return locationSpecs
    if ogc_name == "Things":
        return thingSpecs
    if ogc_name == "ObservedProperties":
        return observedPropertySpecs
    if ogc_name == "DataStreams":
        return dataStreamSpecs
    if ogc_name == "Observations":
        return observationSpecs
    if ogc_name == "FeaturesOfInterest":
        return featureOfInterestSpecs
