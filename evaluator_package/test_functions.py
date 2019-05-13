from ogc_utility import *
from test_utility import create_records_file
from environments import test_env
import functools
from . import evaluating_conditions as conditions


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


@conditions.needed_fields(["create"], critical_failures_resistant=False)
def create_test_records(evaluator):
    if evaluator.args.session:
        evaluator.args.create["file"] = "test_files/" + evaluator.args.create["type"]
        result = create_records_file(args_to_dict(evaluator.args.create))
        evaluator.environment["testing_items"][evaluator.args.create["type"]]\
            .append(result["created_name_list"])
    else:
        evaluator.environment["non_critical_failures"].append("Error: impossible create test items"
                                                              "if session is not started")
