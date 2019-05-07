from ogc_utility import *
from test_utility import create_records_file
from environments import test_env


def clear_test_environment(args, environment):
    temp_address = environment["GOST_address"]
    temp_mode = environment["mode"]
    temp_testing_items = environment["testing_items"]

    if args.session == "delete":
        print("cleared session")
        for ogc_type in temp_testing_items:
            for i in ogc_type:
                delete_item(i["name"], ogc_type, environment) # TODO
        temp_testing_items = []

    environment = test_env(GOST_address=temp_address, mode=temp_mode,
                           testing_items=temp_testing_items)
    return environment


def started_session(args, environment):
    if args.session == "start":
        print("started test session")
    return environment


def create_test_records(args, environment):
    if args.create:
        if args.start_session:
            result = create_records_file(args_to_dict(args.create))
            environment["testing_items"].append(result[0])
        else:
            errors = create_records_file(args_to_dict(args.create))[1]
            environment["non_critical_failures"].append(errors)
    return environment
