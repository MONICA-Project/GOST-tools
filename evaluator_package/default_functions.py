from ogc_utility import *
import pprint
from json import JSONDecoder, JSONDecodeError
import re
from test_utility import create_records_file
from environments import default_env
import shlex


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
                        evaluator.environment["selected_items"].append(get_item(get_identifier,
                                                                                evaluator.args.ogc,
                                                                                evaluator.environment))

                if evaluator.args.identifier:
                    for current_identifier in evaluator.args.identifier:
                        evaluator.environment["selected_items"].append(get_item(current_identifier,
                                                                                evaluator.args.ogc,
                                                                                evaluator.environment))


def select_items(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.args.select:
            select_rules = args_to_dict(evaluator.args.select)
            for x in evaluator.environment["selected_items"].copy():
                if not all_matching_fields(x, select_rules):
                    evaluator.environment["selected_items"].remove(x)


def select_fields(evaluator):
    if not evaluator.environment["critical_failures"]:

        if evaluator.args.fields:
            for x in evaluator.environment["selected_items"]:
                for field in x.copy():
                    if not field in evaluator.args.fields:
                        x.pop(field, None)


def delete(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.args.delete:
            temp_list = []
            for x in evaluator.environment["selected_items"]:
                try:
                    if "error" in x:
                        evaluator.environment["non_critical_failures"].append(x["error"])
                    elif "@iot.id" in x:
                        delete_item(x.get("@iot.id"), evaluator.args.ogc, evaluator.environment)
                        temp_list.append("Deleted id: " + str(x.get("@iot.id")))
                except AttributeError as attr:
                    print(attr)
                    pass
            evaluator.environment["selected_items"] = temp_list


def patch(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.args.patch:
            for x in evaluator.environment["selected_items"]:
                if not ("error" in x) and ("@iot.id" in x):
                    patches = args_to_dict(evaluator.args.patch)
                    evaluator.environment["results"].append(patch_item(patches, str(x.get("@iot.id")),
                                                             evaluator.args.ogc, evaluator.environment).json())


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
                        if "error" in json_result:
                            evaluator.environment["non_critical_failures"].append(json_result["error"])
                        else:
                            evaluator.environment["selected_items"].append(json_result)


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
            evaluator.environment["critical_failures"].append("This command needs an ogc type (--ogc <type name>)")


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
            if len(evaluator.args.GOSTaddress[0]) < 8:
                evaluator.environment["critical_failures"].append("error: invalid address")
            else:
                evaluator.environment["GOST_address"] \
                    = connection_config.set_GOST_address(evaluator.args.GOSTaddress[0])


def show_failures(evaluator):
    if evaluator.environment["critical_failures"]:
        print("critical_failures:")
        for x in evaluator.environment["critical_failures"]:
            print(x)
    if evaluator.environment["non_critical_failures"]:
        print("non_critical_failures:")
        for x in evaluator.environment["non_critical_failures"]:
            print(x)


def show_results(evaluator):
    if not evaluator.environment["critical_failures"]:
        if evaluator.environment["selected_items"]:
            print("selected items:")
            pp = pprint.PrettyPrinter(indent=4)
            for x in evaluator.environment["selected_items"]:
                pp.pprint(x)
        if evaluator.environment["results"]:
            print("results:")
            pp = pprint.PrettyPrinter(indent=4)
            for x in evaluator.environment["results"]:
                pp.pprint(x)


def create_records(evaluator):
    if evaluator.args.create:
        errors = create_records_file(args_to_dict(evaluator.args.create))[1]
        evaluator.environment["non_critical_failures"].append(errors)


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
    from .evaluator import EvaluatorClass  # late import for avoiding cross-import problems
    file_evaluator = EvaluatorClass(["-i"], reading_file = True)
    file = open(file_name)
    requests_list = file.readlines()
    for request in requests_list:
        file_evaluator.evaluate(shlex.split(request))
    file.close()
