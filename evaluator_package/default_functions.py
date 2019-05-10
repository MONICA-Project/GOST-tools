from ogc_utility import *
import pprint
from json import JSONDecoder, JSONDecodeError
import re
from test_utility import create_records_file
from environments import default_env
import shlex
import copy


def get_info(evaluator):
    if evaluator.args.info:
        if evaluator.environment["mode"]:
            print("Mode : " + str(evaluator.environment["mode"]))
        if evaluator.environment["GOST_address"]:
            print("Address : " + evaluator.environment["GOST_address"])


def get(evaluator):
    if not evaluator.environment["critical_failures"]:
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


def select_items(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.args.select:

            boolean_mode = "and"

            if (evaluator.args.select[0] == "and") or (evaluator.args.select[0] == "or"):
                boolean_mode = evaluator.args.select[0]
                evaluator.args.select = evaluator.args.select[1:]

            select_rules = args_to_dict(evaluator.args.select)
            for x in evaluator.environment["selected_items"].copy():
                res = matching_fields(x, select_rules, boolean_mode)
                if not res:
                    evaluator.environment["selected_items"].remove(x)
            if len(evaluator.environment["selected_items"]) == 0:
                evaluator.environment["non_critical_failures"] += [f"error: no {evaluator.args.ogc} found " \
                    f"with select statement conditions"]


def select_result_fields(evaluator):
    if not evaluator.environment["critical_failures"]:
        if not evaluator.environment["results"] and only_get(evaluator.args):
            # if the user has only made a get request, the results
            # are simply the selected items

            evaluator.environment["results"] = \
                copy.deepcopy(evaluator.environment["selected_items"])

        if evaluator.args.show:
            if "all" not in evaluator.args.show:
                for x in evaluator.environment["results"]:
                    for field in x.copy():
                        if field not in evaluator.args.show:
                            x.pop(field, None)


def delete(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.args.delete:
            if evaluator.environment["selected_items"]:  # deleting selected items

                warning_message = f"You are going to delete the {evaluator.args.ogc} " \
                    f"with the following id:\n"   # creation of warning message
                for x in evaluator.environment["selected_items"]:
                    try:
                        if "error" in x:
                            pass
                        elif "@iot.id" in x:
                            id = str(x["@iot.id"])
                            warning_message += id + " "
                    except AttributeError as attr:
                        print("missing" + attr)
                        pass
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


def patch(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.args.patch:
            for x in evaluator.environment["selected_items"]:
                if ("error" not in x) and ("@iot.id" in x):
                    patches = args_to_dict(evaluator.args.patch)
                    result = patch_item(patches, str(x.get("@iot.id")),
                                evaluator.args.ogc, evaluator.environment).json()
                    append_result(evaluator, result, "results")


def post(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.args.post:
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


def connection_test(evaluator):
    if not evaluator.environment["critical_failures"]:

        if not connection_config.test_connection(evaluator.environment.GOST_address, False):
            print("Network error, failed connection")
            evaluator.environment["critical_failure"].append("failed connection "
                                                             "to " + evaluator.environment["GOST_address"][:-5])
        else:
            print(f"current GOST address: {evaluator.environment.GOST_address}\n'--address <ip:port>' to change")


def exit_function(evaluator):
    if evaluator.reading_file:
        pass
    elif evaluator.args.exit:
        exit(0)


def missing_ogc_type(evaluator):
    """returns True if the submitted command requires
    one or more OGC item type and they are not provided"""
    if not evaluator.environment["critical_failures"]:
        needed_ogc_type = evaluator.args.get or evaluator.args.delete \
                          or evaluator.args.patch or evaluator.args.post
        missing_ogc = needed_ogc_type and (not evaluator.args.ogc)
        if missing_ogc:
            evaluator.environment["critical_failures"].append("This command needs an ogc type "
                                                              "(--ogc <type name>)")


def execute_and_exit(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.args.interactive:
            print("Entering interactive mode: --exit to return to shell")
        elif evaluator.reading_file:
            pass
        else:
            exit(0)


def ping(evaluator):
    if evaluator.args.pingconnection:
        if evaluator.environment["GOST_address"]:
            connection_config.test_connection(evaluator.environment["GOST_address"][:-5], verbose=True)
        else:
            evaluator.environment["non_critical_failures"].append("GOST address undefined, ping not possible")


def saved_address(evaluator):
    if not evaluator.environment["critical_failures"]:
        evaluator.environment["GOST_address"] = connection_config.set_GOST_address()
        if not evaluator.environment["GOST_address"]:
            evaluator.environment["critical_failures"].append("error: invalid address")


def user_defined_address(evaluator):
    if not evaluator.environment["critical_failures"]:

        if evaluator.args.GOSTaddress:
            if len(evaluator.args.GOSTaddress) < 8:
                evaluator.environment["critical_failures"].append("error: invalid address")
            else:
                valid_conn = connection_config.set_GOST_address(evaluator.args.GOSTaddress)
                if not valid_conn:
                    evaluator.environment["critical_failures"].append("error: address not working")
                else:
                    evaluator.environment["GOST_address"] = valid_conn


def show_failures(evaluator):
    if evaluator.environment["critical_failures"]:
        print("critical_failures("
                  + str(len(evaluator.environment["critical_failures"])) + "):")
        for x in evaluator.environment["critical_failures"]:
            print(x)
    if evaluator.environment["non_critical_failures"]:
        print("non_critical_failures("
                  + str(len(evaluator.environment["non_critical_failures"])) + "):")
        for x in evaluator.environment["non_critical_failures"]:
            print(x)


def show_results(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.environment["results"]:
            print("results("
                  + str(len(evaluator.environment["results"])) + "):")
            pp = pprint.PrettyPrinter(indent=4)
            for x in evaluator.environment["results"]:
                pp.pprint(x)


def create_records(evaluator):
    if evaluator.args.create:
        result = create_records_file(args_to_dict(evaluator.args.create))
        if result["errors"]:
            evaluator.environment["non_critical_failures"] += result["errors"]
        if evaluator.args.show:
            if result["created_name_list"]:
                evaluator.environment["results"] += result["created_name_list"]


def read_file(evaluator):
    """creates a temporary evaluator_package which evaluates the instructions
    in the file specified by args.file"""
    # TODO recursion control
    if evaluator.args.file:
        file_iterator(evaluator.args.file)


def clear_environment(evaluator):
    temp_address = evaluator.environment["GOST_address"]
    temp_mode = evaluator.environment["mode"]
    evaluator.environment = default_env(GOST_address=temp_address, mode=temp_mode)


def format_multi_options(args):
    for key in args.__dict__:
        string_arg = args.__dict__[key]
        if not (key == "identifier" or key == "ogc") and isinstance(string_arg, str):  # accepts only one ogc type
                                                                                       # for each query
            args.__dict__[key] = string_arg.split()

    return args


def file_iterator(file_name):
    from evaluator_package.evaluator import EvaluatorClass  # late import for avoiding cross-import problems
    file_evaluator = EvaluatorClass(["-i"], reading_file = True)
    file = open(file_name)
    requests_list = file.readlines()
    for request in requests_list:
        file_evaluator.evaluate(shlex.split(request))
    file.close()


def append_result(evaluator, result, field_name):
    """appends the 'result' dict to 'field_name' of evaluator, after having checked
    if an error field exists in 'result',
    in which case the result is appended to 'non_critical_failures'"""
    if "error" in result:
        evaluator.environment["non_critical_failures"].append(result)
    else:
        evaluator.environment[field_name].append(result)


def only_get(args):
    """checks if the only user command is get"""
    args_dict = args.__dict__
    if args_dict["get"]:
        for key in args_dict:
            if (key == "identifier") or (key == "ogc") or (key == "get"):
                pass
            if not bool(key):
                return False
        return True
    return False

