import checking_functions as check

sensorSpecs = {"name": check.sensor_is_already_present, "description": check.field_is_void}
thingSpecs = {"name": check.thing_is_already_present}
observedPropertySpecs = {"name": check.observed_property_is_already_present}
dataStreamSpecs = {"name": check.data_stream_is_already_present}
observationSpecs = {}
locationSpecs = {"name": check.location_is_already_present}
featureOfInterestSpecs = {"name": check.feature_of_interest_is_already_present}

"""It provides the specs of the OGC type that you need"""


def get_specs(ogc_name):
    """return: OGC type that it serves"""
    if ogc_name == "Sensors":
        return sensorSpecs
    if ogc_name == "Locations":
        return locationSpecs
    if ogc_name == "Things":
        return thingSpecs
    if ogc_name == "ObservedProperties":
        return observedPropertySpecs
    if ogc_name == "DataStreams" or ogc_name == "Datastreams":
        return dataStreamSpecs
    if ogc_name == "Observations":
        return observationSpecs
    if ogc_name == "FeaturesOfInterest":
        return featureOfInterestSpecs
