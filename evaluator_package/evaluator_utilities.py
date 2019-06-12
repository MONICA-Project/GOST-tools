def ask_ogc(evaluator):
    """Asks the user for a valid entity type and stores it in evaluator.args.ogc"""

    provided_ogc = input("Missing or invalid Ogc Type, insert one or 'exit' to exit: \n")
    if is_ogc(provided_ogc):
        evaluator.args.ogc = provided_ogc
        return True
    if is_ogc(provided_ogc + "s"):
        evaluator.args.ogc = provided_ogc + "s"
        return True
    if provided_ogc == 'exit':
        exit(0)
    else:
        while not (is_ogc(provided_ogc) or is_ogc(provided_ogc + "s")):
            provided_ogc = input("Invalid Ogc Type, insert one or 'exit' to exit:\n"
                                 "(the types are Things, Sensors, Locations, HystoricalLocations, Datastreams, "
                                 "ObservedProperties, Observations, FeaturesOfInterest)\n")

            if provided_ogc == 'exit':
                exit(0)
    if is_ogc(provided_ogc):
        evaluator.args.ogc = provided_ogc
        return True
    if is_ogc(provided_ogc + "s"):
        evaluator.args.ogc = provided_ogc + "s"
        return True


def is_ogc(name):
    """Checks if name is a valid ogc entity type"""

    return name in ["Things", "Sensors", "Locations", "HystoricalLocations", "Datastreams", "ObservedProperties",
                    "Observations", "FeaturesOfInterest"]


def check_and_fix_ogc(evaluator):
    """check if ogc_type is only missing the final 's', in that case automatically fix it,
    otherwise asks the user to insert a valid ogc type"""

    if bool(evaluator.args.ogc):
        ogc_pluralized = evaluator.args.ogc + "s"
        if is_ogc(ogc_pluralized):
            evaluator.args.ogc = ogc_pluralized
            return True
        elif is_ogc(evaluator.args.ogc):
            return True
        elif not is_ogc(evaluator.args.ogc):
            return ask_ogc(evaluator)
    else:
        return ask_ogc(evaluator)


def check_name_duplicates(evaluator, list_name):
    """find name duplicates in given list"""

    names_list = []
    for i in evaluator.environment[list_name]:
        if "name" in i:  # necessary for nameless entities like Observations
            names_list.append(i["name"])
    duplicate_dict = {}
    for j in names_list:
        if j in duplicate_dict:
            duplicate_dict[j] += 1
        else:
            duplicate_dict[j] = 1

    for key, val in duplicate_dict.items():
        if val > 1:
            error_message = {"error": f"found {str(val)} records with name {key}"}
            evaluator.environment["critical_failures"].append(error_message)
