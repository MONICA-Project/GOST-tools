from ogc_utility import *
import pprint
from json import JSONDecoder, JSONDecodeError
import re
from creation_utilities import create_records_file
from evaluator_package.environments import default_env
import shlex
import copy
from . import evaluating_conditions_decorator as conditions
from . import evaluator_utilities
from . import selection_parser



@conditions.needed_fields(at_least_one_field=["info"], all_mandatory_fields=[],
                          critical_failures_resistant=True)
def get_info(evaluator):
    """prints the informations about the current evaluator"""
    if evaluator.environment["mode"]:
        print("Mode : " + str(evaluator.environment["mode"]))
    if evaluator.environment["GOST_address"]:
        print("Address : " + evaluator.environment["GOST_address"])


@conditions.needed_fields(at_least_one_field=["get"], needed_ogc=True,
                          critical_failures_resistant=False)
def get_command_line(evaluator):
    """gets the items from GOST, used if get or identifier are defined"""
    get(evaluator)


@conditions.needed_fields(at_least_one_field=["select"], critical_failures_resistant=False)
def select_items_command_line(evaluator):
    """selects the items matching with the rules defined in evaluator.args.select
    and removes the others"""
    if (bool(evaluator.args.patch) or bool(evaluator.args.delete)) and not bool(evaluator.args.get):
        return False
    else:
        select_items(evaluator)


@conditions.needed_fields(at_least_one_field=["show", "get"], critical_failures_resistant=False)
def select_result_fields(evaluator):
    """selects which fields of the record in result will be showed.
    If get is defined but there is no result, all the getted items will be
    showed"""
    if not evaluator.environment["results"] and only_get(evaluator.args):
        # if the user has only made a get request, the results
        # are simply the selected items

        evaluator.environment["results"] = copy.deepcopy(evaluator.environment["selected_items"])

    if evaluator.args.show:
        if "all" not in evaluator.args.show:
            for x in evaluator.environment["results"]:
                for field in x.copy():
                    if field not in evaluator.args.show:
                        x.pop(field, None)


@conditions.needed_fields(all_mandatory_fields=["delete"], critical_failures_resistant=False,
                          needed_ogc=True)
def delete(evaluator):
    """delete from GOST bb the items selected with get:
    befor deleting asks user for confirmation"""
    get_without_line_command(evaluator)
    if evaluator.environment["selected_items"]:  # deleting selected items
        warning_message = f"You are going to delete the {evaluator.args.ogc} " \
            f"with the following name and id:\n"   # creation of warning message
        for x in evaluator.environment["selected_items"]:
            try:
                if "error" in x:
                    pass
                elif "@iot.id" in x:
                    warning_message +=  str(x["@iot.id"]) + " " +  str(x["name"]) + "\n"
            except AttributeError as attr:
                print("missing" + attr)
                pass
        for x in evaluator.environment["non_critical_failures"]:
            if "error" in x:
                print(x["error"]["message"])

        proceed = input(warning_message + "\nProceed?(y/N)")

        if proceed == "y":  # elimination of items
            for x in evaluator.environment["selected_items"]:
                try:
                    if "error" in x:
                        evaluator.environment["non_critical_failures"].append(x["error"])
                    elif "@iot.id" in x:
                        result = delete_item(x.get("@iot.id"), evaluator.args.ogc, evaluator.environment)
                        append_result(evaluator, result, "results")
                except AttributeError as attr:
                    print("missing" + attr)
                    pass
        else:
            print("Aborted deletion")
    else:
        print("trying to delete but no item defined")


@conditions.needed_fields(all_mandatory_fields=["patch"], critical_failures_resistant=False,
                          needed_ogc=True)
def patch(evaluator):
    """
    patches the selected fields of the items chosen with get with the selected values
    """
    get_without_line_command(evaluator)
    for x in evaluator.environment["selected_items"]:
        if ("error" not in x) and ("@iot.id" in x):
            patches = args_to_dict(evaluator.args.patch)
            result = patch_item(patches, str(x.get("@iot.id")), evaluator.args.ogc, evaluator.environment)
            append_result(evaluator, result, "results")


@conditions.needed_fields(at_least_one_field=["post"], critical_failures_resistant=False,
                          needed_ogc=True)
def post(evaluator):
    for file in evaluator.args.post:
        with open(file) as json_file:
            NOT_WHITESPACE = re.compile(r'[^\s]')
            def decode_stacked(document, pos=0, decoder=JSONDecoder()):
                while True:
                    match = NOT_WHITESPACE.search(document, pos)
                    if not match:
                        return
                    pos = match.start()

                    try:
                        obj, pos = decoder.raw_decode(document, pos)
                    except JSONDecodeError:
                        raise
                    yield obj

            for obj in decode_stacked(json_file.read()):
                result = add_item(obj, evaluator.args.ogc)
                json_result = json.loads((result.data).decode('utf-8'))
                append_result(evaluator, json_result, "results")


@conditions.needed_fields(at_least_one_field=[], critical_failures_resistant=False)
def connection_test(evaluator):
    if not connection_config.test_connection(evaluator.environment.GOST_address, False):
        print("Network error, failed connection")
        evaluator.environment["critical_failure"].append("failed connection "
                                                         "to " + evaluator.environment["GOST_address"][:-5])
    else:
        print(f"current GOST address: {evaluator.environment.GOST_address}\n'--address <ip:port>' to change")


@conditions.needed_fields(critical_failures_resistant=True)
def exit_function(evaluator):
    if evaluator.reading_file:
        pass
    elif evaluator.args.exit:
        exit(0)


@conditions.needed_fields(at_least_one_field=[], critical_failures_resistant=False)
def execute_and_exit(evaluator):
    if evaluator.args.interactive:
        print("Entering interactive mode: --exit to return to shell")
    elif evaluator.reading_file:
        pass
    else:
        exit(0)


@conditions.needed_fields(at_least_one_field=["pingconnection"], critical_failures_resistant=True)
def ping(evaluator):
    if evaluator.environment["GOST_address"]:
        connection_config.test_connection(evaluator.environment["GOST_address"][:-5], verbose=True)
    else:
        evaluator.environment["non_critical_failures"].append("GOST address undefined, ping not possible")


@conditions.needed_fields(no_fields=["GOSTaddress"],at_least_one_field=[],
                          all_mandatory_fields=[], critical_failures_resistant=False)
def saved_address(evaluator):
    """checks if there is a saved address, and tries to connect to it.
    This method is intended only for the first evaluation of the session"""
    evaluator.environment["GOST_address"] = connection_config.set_GOST_address()
    if not evaluator.environment["GOST_address"]:
        evaluator.environment["critical_failures"].append("error: GOST address missing or not working")


@conditions.needed_fields(at_least_one_field=["GOSTaddress"], critical_failures_resistant=False)
def user_defined_address(evaluator, verbose = True):
    """if the user has defined a GOST address, checks if it is possible to reach it.
    If it possible, sets the GOST address to the new address, otherwise asks the user if he
    wants to select a different address or wants to keep the non working address"""
    working_conn = connection_config.test_connection((evaluator.args.GOSTaddress)[:-5])
    if working_conn:
        valid_conn = connection_config.set_GOST_address(evaluator.args.GOSTaddress)
        evaluator.environment["GOST_address"] = valid_conn
    else:
        warning_message = f"The selected GOST address is not working, " \
            f"do you want to set it as your address or want to change it?\n" \
            f"'y' to set the currently provided address\n'ch' to set a new address\n" \
            f"'n' to mantain the old address:\n"  # creation of warning message
        proceed = input(warning_message)
        if proceed == "y":
            valid_conn = connection_config.set_GOST_address(evaluator.args.GOSTaddress)
            evaluator.environment["GOST_address"] = valid_conn
        elif proceed == "ch":
            new_address = input("Insert new address:\n")
            evaluator.args.GOSTaddress = new_address
            user_defined_address(evaluator)

        else:
            evaluator.environment["GOST_address"] = connection_config.set_GOST_address()
            if not evaluator.environment["GOST_address"]:
                evaluator.environment["critical_failures"].append("error: GOST address not defined")


@conditions.needed_fields(at_least_one_field=[], critical_failures_resistant=True)
def show_failures(evaluator):
    """shows the failures occurred during evaluation"""
    if evaluator.environment["critical_failures"]:
        for x in evaluator.environment["critical_failures"]:
            print(x)
        print("Found "+ str(len(evaluator.environment["critical_failures"])) + " critical_failures\n")

    if evaluator.environment["non_critical_failures"]:
        for x in evaluator.environment["non_critical_failures"]:
            print(x)
        print("Found " + str(len(evaluator.environment["non_critical_failures"])) + " non_critical_failures\n")


@conditions.needed_fields(at_least_one_field=[], critical_failures_resistant=False)
def show_results(evaluator):
    """shows the results of evaluation"""
    if evaluator.environment["results"]:
        pp = pprint.PrettyPrinter(indent=4)
        for x in evaluator.environment["results"]:
            pp.pprint(x)
        print(str(len(evaluator.environment["results"])) + " results found\n")


@conditions.needed_fields(at_least_one_field=["create"], critical_failures_resistant=False,
                          needed_ogc=True)
def create_records(evaluator):
    """create records to store in a file"""
    create_without_line_command(evaluator)


@conditions.needed_fields(at_least_one_field=["read_file"], critical_failures_resistant=False)
def read_file(evaluator):
    """creates a temporary evaluator_package which evaluates the instructions
    in the file specified by args.file"""
    # TODO recursion control
    if evaluator.args.file:
        file_iterator(evaluator.args.file)


def clear_environment(evaluator):
    """clear the environment between different requests in the same session in default mode"""
    temp_address = evaluator.environment["GOST_address"]
    temp_mode = evaluator.environment["mode"]
    evaluator.environment = default_env(GOST_address=temp_address, mode=temp_mode)


def format_multi_options(args):
    """takes a dictionary and stores each key's value as a list
    example: {"get" : "102 103"} becomes {"get" : [102] [103]}
    {"get" : "102 '103 104'"} becomes {"get" : [102] [103 104]}"""
    for key in args.__dict__:
        string_arg = args.__dict__[key]
        if not (key == "ogc") and isinstance(string_arg, str):  # accepts only one ogc type
                                                                                       # for each query
            args.__dict__[key] = evaluator_utilities.custom_split(args.__dict__[key], ['"'])
    return args


def file_iterator(file_name):
    from evaluator_package.evaluator import EvaluatorClass  # late import for avoiding cross-import problems
    file_evaluator = EvaluatorClass(["-i"], reading_file = True)
    file = open(file_name)
    requests_list = file.readlines()
    for request in requests_list:
        file_evaluator.evaluate(shlex.split(request))
    file.close()


def append_result(evaluator, result, field_name="results", failure_type = "non_critical_failures"):
    """appends the 'result' dict to 'field_name' of evaluator, after having checked
    if an error field exists in 'result',
    in which case the result is appended to failure_type"""
    if "error" in result:
        evaluator.environment[failure_type].append(result)
    else:
        evaluator.environment[field_name].append(result)


def only_get(args):
    """checks if the only user command involving items is get"""
    args_dict = args.__dict__
    if args_dict["get"]:
        for key in args_dict:
            if (key == "delete") or (key == "patch"):
                if bool(args_dict[key]):
                    return False
        return True
    return False


def get(evaluator):
    """gets the items from GOST, used as auxilliary method by other commands"""
    if evaluator.args.identifier == ["all"] or ((not evaluator.args.identifier)
                                                and evaluator.args.get):
        results = get_all(evaluator.args.ogc, evaluator.environment)
        evaluator.environment["selected_items"] = results

    else:
        if evaluator.args.get:
            if type(evaluator.args.get) is list:
                for get_identifier in evaluator.args.get:
                    result = get_item(get_identifier, evaluator.args.ogc, evaluator.environment)
                    append_result(evaluator, result, "selected_items")

            if evaluator.args.identifier:
                for current_identifier in evaluator.args.identifier:
                    result = get_item(current_identifier, evaluator.args.ogc, evaluator.environment)
                    append_result(evaluator, result, "selected_items")

    evaluator_utilities.check_name_duplicates(evaluator, "selected_items")
    evaluator_utilities.check_name_duplicates(evaluator, "results")


def get_without_line_command(current_evaluator):
    """get the items in identifier and stores them in selected items even if get is not defined"""
    if current_evaluator.args.identifier:
        for i in current_evaluator.args.identifier:
            get_result = get_item(i, current_evaluator.args.ogc, current_evaluator.environment)
            append_result(current_evaluator, get_result, field_name="selected_items")
    else:
        result_all = get_all(current_evaluator.args.ogc, current_evaluator.environment)
        for i in result_all:
            append_result(current_evaluator, i, field_name="selected_items")

        select_items(current_evaluator)
        evaluator_utilities.check_name_duplicates(current_evaluator, "selected_items")


def select_items(evaluator):
    for single_item in evaluator.environment["selected_items"].copy():
        matching = selection_parser.select_parser(evaluator.args.select, single_item)
        if not matching:
            evaluator.environment["selected_items"].remove(single_item)
    if len(evaluator.environment["selected_items"]) == 0:
        evaluator.environment["non_critical_failures"] += [f"error: no {evaluator.args.ogc} found "
                                                           f"with select statement conditions"]


def create_without_line_command(evaluator):
    result = create_records_file(args_to_dict(evaluator.args.create), evaluator.args.ogc)
    if result["errors"]:
        evaluator.environment["non_critical_failures"] += result["errors"]
    if evaluator.args.show:
        if result["created_name_list"]:
            evaluator.environment["results"] += result["created_name_list"]