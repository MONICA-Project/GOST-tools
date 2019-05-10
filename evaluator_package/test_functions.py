from ogc_utility import *
from test_utility import create_records_file
from environments import test_env


def clear_test_environment(evaluator):
    temp_address = evaluator.environment["GOST_address"]
    temp_mode = evaluator.environment["mode"]
    temp_testing_items = evaluator.environment["testing_items"]

    if evaluator.args.session == "delete":
        print("cleared session")
        for ogc_type in temp_testing_items:
            for i in ogc_type:
                delete_item(i["name"], ogc_type, evaluator.environment) # TODO
        temp_testing_items = []

    evaluator.environment = test_env(GOST_address=temp_address, mode=temp_mode,
                                     testing_items=temp_testing_items)


def started_session(evaluator):
    if evaluator.args.session == "start":
        print("started test session")


def create_test_records(evaluator):
    if evaluator.args.create:
        if evaluator.args.start_session:
            result = create_records_file(args_to_dict(evaluator.args.create))
            evaluator.environment["testing_items"].append(result["created_name_list"])
        else:
            errors = create_records_file(args_to_dict(evaluator.args.create))["errors"]
            evaluator.environment["non_critical_failures"].append(errors)
