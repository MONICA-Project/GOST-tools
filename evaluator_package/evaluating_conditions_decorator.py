from . import evaluator_utilities
from ogc_utility import *
from . import selection_parser
import shlex


def needed_fields(no_fields=None,at_least_one_field=None,
                  all_mandatory_fields=None, critical_failures_resistant=False,
                  needed_ogc=False, needed_items = False):
    """Decorator: checks conditions before executing the decorated function.


    :param no_fields: ([str]): the field(s) which presence in current command string
                           negate the execution of the function
    :param at_least_one_field: ([str]): the field(s) for which the presence of at least
                            one of them in the current command string
                            is mandatory for the execution of the function

    :param all_mandatory_fields: ([str]): the field(s) the presence of all of them in the current
                            command string is mandatory for the execution of the function

    :param critical_failures_resistant: if True, the function will be
                            executed regardless of the presence of critical failures,
                            otherwise not
    :param needed_ogc: if True, the command string will be checked for an ogc type:
                        if not found, the user will be asked to provide one

    :param needed_items: if True, the current environment will be checked for selected items:
                        if not found, a get with the parameters provided in command string
                        will be executed on GOST
    :return: False if the function is not executed
    """
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
    """Makes a get on GOST based upon current_evaluator args and environment


    :param current_evaluator: if current_evaluator.args contains the fields and values
                              needed to identify an item(s) and there aren't items already selected,
                              the query is executed and eventually filtered by --select statement
                              arguments, if provided. The result is appended
                              to current_evaluator.environment["selected_items"]
    :return:
    """

    if not bool(current_evaluator.environment["selected_items"]):  # necessary to avoid getting items more than one time
        if bool(current_evaluator.args.identifier):
            for i in current_evaluator.args.identifier:
                get_result = get_item(i, current_evaluator.args.ogc, current_evaluator.environment)
                add_result(current_evaluator, get_result, field_name="selected_items")
        else:
            evaluator_utilities.check_and_fix_ogc(current_evaluator)
            result_all = get_all(current_evaluator.args.ogc, current_evaluator.environment)
            for i in result_all:
                add_result(current_evaluator, i, field_name="selected_items")
        select_items(current_evaluator)
        evaluator_utilities.check_name_duplicates(current_evaluator, "selected_items")


def add_result(evaluator, result, field_name="results", failure_type ="non_critical_failures"):
    """

    :param evaluator:
    :param result:
    :param field_name:
    :param failure_type:
    :return:
    """
    if "error" in result:
        evaluator.environment[failure_type].append(result)
    else:
        evaluator.environment[field_name].append(result)


def select_items(evaluator):
    """

    :param evaluator:
    :return:
    """
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
