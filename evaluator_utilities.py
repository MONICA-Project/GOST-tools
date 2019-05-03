from ogc_utility import *
import pprint
from json import JSONDecoder, JSONDecodeError
import re
from test_utility import create_records_file


def get_info(args, environment):
    if args.info:
        if environment["mode"]:
            print("Mode : " + str(environment["mode"]))
        if environment["GOST_address"]:
            print("Address : " + environment["GOST_address"])
    return environment


def get(args, environment):
    if environment["critical_failures"]:
        return environment

    if args.identifier == ["all"] or ((not args.identifier) and args.get):
        results = get_all(args.ogc, environment)
        environment["selected_items"] = results

    else:
        if args.get:
            if type(args.get) is list:
                for get_identifier in args.get:
                    environment["selected_items"].append(get_item(get_identifier, args.ogc, environment))

            if args.identifier:
                for current_identifier in args.identifier:
                    environment["selected_items"].append(get_item(current_identifier, args.ogc, environment))

    return environment


def select_items(args, environment):
    if environment["critical_failures"]:
        return environment
    if args.select_items:
        select_rules = args_to_dict(args.select)
        for x in environment["selected_items"]:
            if not all_matching_fields(x, select_rules):
                environment["selected_items"].remove(x)
    return environment


def select_fields(args, environment):
    if environment["critical_failures"]:
        return environment

    if args.fields:
        for x in environment["selected_items"]:
            for field in x.copy():
                if not field in args.fields:
                    x.pop(field, None)
    return environment


def delete(args, environment):
    if environment["critical_failures"]:
        return environment

    if args.delete:
        temp_list = []
        for x in environment["selected_items"]:
            try:
                if "error" in x:
                    environment["non_critical_failures"].append(x["error"])
                elif "@iot.id" in x:
                    delete_item(x.get("@iot.id"), args.ogc, environment)
                    temp_list.append("Deleted id: " + str(x.get("@iot.id")))
            except AttributeError as attr:
                print(attr)
                pass
        environment["selected_items"] = temp_list
    return environment


def patch(args, environment):
    if environment["critical_failures"]:
        return environment
    if args.patch:
        for x in environment["selected_items"]:
            if not ("error" in x) and ("@iot.id" in x):
                patch_item(args_to_dict(args.patch), str(x.get("@iot.id")), args.ogc, environment)
    return environment


def post(args, environment):
    if environment["critical_failures"]:
        return environment
    if args.post:
        for file in args.post:
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
                    result = add_item(obj, args.ogc)
                    json_result = json.loads((result.data).decode('utf-8'))
                    if "error" in json_result:
                        environment["non_critical_failures"].append(json_result["error"])
                    else:
                        environment["selected_items"].append(json_result)

    return environment


def connection_test(args, environment):
    if environment["critical_failures"]:
        return environment

    if not connection_config.test_connection(environment.GOST_address, False):
        print("Network error, failed connection")
        environment["critical_failure"].append("failed connection to " + environment["GOST_address"][:-5])
    else:
        print(f"current GOST address: {environment.GOST_address}\n'--address <ip:port>' to change")
    return environment


def exit_function(args, environment):
    if args.exit:
        exit(0)
    return environment


def missing_ogc_type(args, environment):
    """returns True if the submitted command requires
    one or more OGC item type and they are not provided"""
    if environment["critical_failures"]:
        return environment

    needed_ogc_type = args.get or args.delete or args.patch or args.post
    missing_ogc = needed_ogc_type and (not args.ogc)
    if missing_ogc:
        environment["critical_failures"].append("This command needs an ogc type (--ogc <type name>)")
    return environment


def execute_and_exit(args, environment):
    if environment["critical_failures"]:
        return environment
    if args.interactive:
        print("Entering interactive mode: --exit to return to shell")
        return environment
    else:
        exit(0)


def ping(args, environment):
    if args.pingconnection:
        if environment["GOST_address"]:
            connection_config.test_connection(environment["GOST_address"][:-5], verbose=True)
        else:
            environment["non_critical_failures"].append("GOST address undefined, ping not possible")
    return environment


def saved_address(args, environment):
    if environment["critical_failures"]:
        return environment
    environment["GOST_address"] = connection_config.set_GOST_address()
    if not environment["GOST_address"]:
        environment["critical_failures"].append("error: invalid address")
    return environment


def user_defined_address(args, environment):
    if environment["critical_failures"]:
        return environment

    if args.GOSTaddress:
        if len(args.GOSTaddress[0]) < 8:
            environment["critical_failures"].append("error: invalid address")
        else:
            environment["GOST_address"] = connection_config.set_GOST_address(args.GOSTaddress[0])
    return environment


def show_failures(args, environment):
    if environment["critical_failures"]:
        print("critical_failures:")
        for x in environment["critical_failures"]:
            print(x)
    if environment["non_critical_failures"]:
        print("non_critical_failures:")
        for x in environment["non_critical_failures"]:
            print(x)
    return environment


def show_results(args, environment):
    if environment["critical_failures"]:
        return environment

    if environment["selected_items"]:
        print("results:")
        pp = pprint.PrettyPrinter(indent=4)
        for x in environment["selected_items"]:
            pp.pprint(x)
    return environment


def create_records(args, environment):
    if args.create:
        create_records_file(args_to_dict(args.create))
    return environment


def clear_environment(args, environment):
    temp_address = environment["GOST_address"]
    temp_mode = environment["mode"]
    environment = {"GOST_address": temp_address, "non_critical_failures": [],
                   "critical_failures": [], "selected_items": [], "mode": temp_mode}
    return environment


def clear_test_environment(args, environment):
    temp_address = environment["GOST_address"]
    temp_mode = environment["mode"]
    environment = {"GOST_address": temp_address, "non_critical_failures": [],
                   "critical_failures": [], "selected_items": [], "mode": temp_mode}
    return environment


def format_multi_options(args):
    for key in args.__dict__:
        string_arg = args.__dict__[key]
        if not (key == "identifier" or key == "ogc") and isinstance(string_arg, str):  # accepts only one ogc type
                                                                                       # for each query
            args.__dict__[key] = string_arg.split()

    return args

