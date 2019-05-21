import re

def custom_split(string, custom_splitters_list):
    """splits a string by whitespace, but ignores the whitespaces inside custom_splitters_list
    example: "custom_splitters_list(a b $c d$ e f, custom_splitters_list=['$']) -> [a][b][c d][e][f]
    If founds two numbers separated by "-", converts them in a list of intermediate number: 1-4 -> [1][2][3][4]
    """
    result = []
    splitted = string.split()
    i = 0

    while i < len(splitted):  # separating by spaces and custom splitter
        if splitted[i] not in custom_splitters_list:
            result.append(splitted[i])
            i += 1
        elif splitted[i] in custom_splitters_list:
            temp_str = ""
            cont_reading = True
            while cont_reading:
                i += 1
                if i >= len(splitted):
                    cont_reading = False
                elif splitted[i] in custom_splitters_list:
                    cont_reading = False
                    i += 1
                else:
                    temp_str += f"{str(splitted[i])}"
                    if splitted[i + 1] not in custom_splitters_list:
                        temp_str += " "

            result.append(temp_str)

    intervals = []
    interval_indexes = []
    for index, value in enumerate(result):  # expanding intervals
        if value == "-": #TODO checking wrong inputs
            lower_bound = result[index - 1] + 1
            upper_bound = result[index + 1] - 1
            for i in range(lower_bound, upper_bound):
                intervals.append(i)
            interval_indexes.append(index)
    for i in interval_indexes:
        result.pop(i)
    result.append(intervals)

    return result


def ask_ogc(evaluator):
    provided_ogc = input("Missing or invalid Ogc Type, insert one or 'exit' to exit: \n")
    if is_ogc(provided_ogc):
        evaluator.args.ogc = provided_ogc
        return True
    if is_ogc(provided_ogc + "s"):
        evaluator.args.ogc = provided_ogc + "s"
        return True
    if provided_ogc == 'exit':
        return False
    else:
        while not (is_ogc(provided_ogc) or is_ogc(provided_ogc + "s")):
            provided_ogc = input("Invalid Ogc Type, insert one or 'exit' to exit:\n"
                                 "(the types are Things, Sensors, Locations, HystoricalLocations, Datastreams, "
                                 "ObservedProperties, Observations, FeaturesOfInterest)\n")
            if provided_ogc == 'exit':
                return False
    if is_ogc(provided_ogc):
        evaluator.args.ogc = provided_ogc
        return True
    if is_ogc(provided_ogc + "s"):
        evaluator.args.ogc = provided_ogc + "s"
        return True


def is_ogc(name):
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

