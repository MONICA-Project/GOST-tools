from . import evaluator_utilities
from ogc_utility import *
from . import selection_parser
import shlex


def needed_fields(no_fields=None,at_least_one_field=None,
                  all_mandatory_fields=None, critical_failures_resistant=False,
                  needed_ogc=False, needed_items = False):
    """decorator with arguments: if at least one of the field in at_least_one
    and  all the fields in all_fields are in args the decorated function is executed,
    otherwise not. If critical_failures_resistant is setted, the function will be
    executed regardless of the presence of critical failures. If ogc is needed but not provided,
    the user will be asked of inserting it. If items are needed but not present,
    a get_items will be executed if the needed_items flag is True"""
    def decorator(function):
        def wrapper(evaluator):
            if bool(evaluator.environment["critical_failures"]) and not critical_failures_resistant:
                return False

            if bool(no_fields):  # checking all field that will block the execution
                for i in no_fields:
                    if bool(evaluator.args.__dict__[i]):
                        return False

            required_at_least = bool(at_least_one_field)
            required_all = bool(all_mandatory_fields)
            required_at_least_confirmed = not required_at_least
            required_all_confirmed = not required_all

            if (not required_all) and (not required_at_least):
                return function(evaluator)

            if required_all:  # checking all mandatory fields
                for i in all_mandatory_fields:
                    if bool(evaluator.args.__dict__[i]):
                        required_all_confirmed = True
                    else:
                        return False

            if required_at_least and bool(evaluator.args.__dict__):  # checking at least one fields
                for i in at_least_one_field:
                    for j in evaluator.args.__dict__:
                        if bool(evaluator.args.__dict__[j]) and (i == j):
                            required_at_least_confirmed = True
                            break

            if required_at_least_confirmed and required_all_confirmed:
                if bool(needed_ogc):
                    if not evaluator_utilities.check_and_fix_ogc(evaluator):
                        evaluator.environment["critical_failures"].append([{"error": "ogc type not defined"}])
                        return False
                if bool(needed_items):
                    get_items(evaluator)
                return function(evaluator)

            else:
                return False

        return wrapper
    return decorator


def get_items(current_evaluator):
    """get the items in identifier and stores them in selected items even if get is not defined"""
    if not bool(current_evaluator.environment["selected_items"]):  # necessary to avoid getting items more than one time
        if bool(current_evaluator.args.identifier):
            for i in current_evaluator.args.identifier:
                get_result = get_item(i, current_evaluator.args.ogc, current_evaluator.environment)
                append_result(current_evaluator, get_result, field_name="selected_items")
        else:
            evaluator_utilities.check_and_fix_ogc(current_evaluator)
            result_all = get_all(current_evaluator.args.ogc, current_evaluator.environment)
            for i in result_all:
                append_result(current_evaluator, i, field_name="selected_items")
        select_items(current_evaluator)
        evaluator_utilities.check_name_duplicates(current_evaluator, "selected_items")


def append_result(evaluator, result, field_name="results", failure_type = "non_critical_failures"):
    """appends the 'result' dict to 'field_name' of evaluator, after having checked
    if an error field exists in 'result',
    in which case the result is appended to failure_type"""
    if "error" in result:
        evaluator.environment[failure_type].append(result)
    else:
        evaluator.environment[field_name].append(result)


def select_items(evaluator):
    if bool(evaluator.environment["selected_items"]):
        for single_item in evaluator.environment["selected_items"].copy():
            matching = selection_parser.select_parser(evaluator.args.select, single_item)
            if not matching:
                evaluator.environment["selected_items"].remove(single_item)
        if len(evaluator.environment["selected_items"]) == 0:
            evaluator.environment["non_critical_failures"] += [f"error: no {evaluator.args.ogc} found "
                                                               f"with select statement conditions"]


def file_iterator(file_name):
    from evaluator_package.evaluator import EvaluatorClass  # late import for avoiding cross-import problems
    file_evaluator = EvaluatorClass(["-i"], reading_file = True)
    file = open(file_name)
    requests_list = file.readlines()
    for request in requests_list:
        file_evaluator.evaluate(shlex.split(request))
    file.close()
