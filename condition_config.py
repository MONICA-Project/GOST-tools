from checking_functions import *

sensorSpecs = {"name": sensor_is_already_present, "description": field_is_void}
thingSpecs = {"name": thing_is_already_present}
observedPropertySpecs = {"name": observed_property_is_already_present}
dataStreamSpecs = {"name": data_stream_is_already_present}
observationSpecs = {}
locationSpecs = {"name": location_is_already_present}
featureOfInterestSpecs = {"name": feature_of_interest_is_already_present}


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
