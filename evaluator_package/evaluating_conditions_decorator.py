from evaluator_package import selection_parser
from evaluator_package.selection_expression_validator import is_field
# from evaluator_package.selection_parser import tokenize_parentheses
from . import evaluator_utilities as eval_util
import ogc_utility as ogc_util
import requests
import shlex
from evaluator_package.environments import default_env
from . import selection_expression_validator
import urllib.parse as urlparse
import connection_config as conn_conf


def needed_fields(no_fields=None, at_least_one_field=None,
                  all_mandatory_fields=None, critical_failures_resistant=False,
                  needed_ogc=False, needed_additional_argument=False, needed_items=False):
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
    :param needed_additional_argument: for the selected values, the user will be asked to insert additional values
                         if no value is provided
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
                    if not eval_util.check_and_fix_ogc(evaluator):
                        evaluator.environment["critical_failures"].append([{"error": "ogc type not defined"}])
                        return False
                if bool(needed_items):
                    get_items(evaluator)

                if bool(check_user_defined_arguments(evaluator, all_mandatory_fields,
                                                     at_least_one_field, needed_additional_argument)):
                    return function(evaluator)
                else:
                    return False
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
    """
    if not bool(current_evaluator.environment["selected_items"]):  # necessary to avoid getting items more than one time
        if bool(current_evaluator.args.identifier):
            for i in current_evaluator.args.identifier:
                get_result = ogc_util.get_item(identifier=i, ogc_type=current_evaluator.args.ogc,
                                               environment=current_evaluator.environment)
                add_result(current_evaluator, get_result, field_name="selected_items")
        else:
            result = eval_util.check_and_fix_ogc(current_evaluator)
            if not result:
                return False
            if current_evaluator.args.select:
                selection_expression_validator.tokenize_parentheses(current_evaluator.args.select)
            result_all = get(current_evaluator.args.ogc, current_evaluator.environment,
                             select_query=current_evaluator.args.select)
            # result_all = get_all(current_evaluator.args.ogc, current_evaluator.environment)
            for i in result_all:
                add_result(current_evaluator, i, field_name="selected_items")
        if not bool(current_evaluator.environment["selected_items"]):
            current_evaluator.environment["non_critical_failures"] += [f"error: no {current_evaluator.args.ogc} found"]
        # else:
        #    select_items(current_evaluator)
        #    evaluator_utilities.check_name_duplicates(current_evaluator, "selected_items")


def get(ogc_type=None, environment=None, payload=None, sending_address=False, select_query=None, ogc_name=None,
        show=None, username=None, password=None):
    result = []
    b = 0  # counter of the element in select_query
    c = 0  # flag to check if the " ' " is open
    z = 0  # flag for identifier
    y = 0  # flag to check if it's necessary to close the " ' "

    gost_address = None
    if environment:
        gost_address = environment["GOST_address"]
        sending_address = gost_address + "/" + ogc_type
    elif not sending_address:
        gost_address = conn_conf.get_address_from_file()
        sending_address = gost_address + "/" + ogc_type
    if not select_query and not show and ogc_name:
        sending_address = gost_address + "/" + ogc_type + "?$filter=name eq '" + ogc_name + "'"
    if select_query and not show:
        sending_address = gost_address + "/" + ogc_type + "?$filter="
        for d in select_query:
            if d is '(':
                sending_address += d
                b += 1
            if is_field(d) and z == 0:
                if d == '@iot.id':
                    sending_address += "id"
                    z = 1
                else:
                    sending_address += d
                    z = 1
                b += 1
            elif d in ["==", "lt", "le", "gt", "ge", "not", "<", "<=", ">", ">="]:
                if d in ["=="]:
                    sending_address += ' eq'
                elif d in ["lt", "<"]:
                    sending_address += ' lt'
                elif d in ["le", "<="]:
                    sending_address += ' le'
                elif d in ["gt", ">"]:
                    sending_address += ' gt'
                elif d in ["ge", ">="]:
                    sending_address += ' ge'
                elif d in ["not"]:
                    sending_address += ' ne'
                sending_address += " '"
                y = 0
                b += 1
                c = 1
            elif d in ["and", "or"] and y == 0:
                sending_address += "' " + d + " "
                z = 0
                b += 1
            elif d in ["and", "or"] and y == 1:
                sending_address += d + " "
                z = 0
                b += 1
            elif (d in ")") and (b <= len(select_query) - 1):
                sending_address += "'" + d + " "
                b += 1
                y += 1
            elif b == len(select_query) - 1:
                sending_address += str(d) + "'"
                b += 1
            elif b != 0 and b < len(select_query) - 1 and c == 0:
                sending_address += " " + str(d)
                b += 1
            elif b != 0 and b < len(select_query) - 1 and c == 1:
                sending_address += str(d)
                b += 1
                c = 0
    elif show and not select_query:
        sending_address = gost_address + "/" + ogc_type + "?$select="
        n = 0
        if len(show) > 1:
            for f in show:
                if n == len(show) - 1:
                    sending_address += f
                else:
                    sending_address += f + ","

    r = requests.get(sending_address, payload, auth=(username, password))
    response = r.json()
    if "value" in response:
        result = response["value"]
    if "@iot.nextLink" in response:  # iteration for getting results beyond first page
        if "GOST_address" not in locals():
            gost_address = sending_address.split("/v1.0")[0]
            gost_address += "/v1.0"
        next_page_address = gost_address + response["@iot.nextLink"].split("/v1.0")[1]
        parsed = urlparse.urlparse(next_page_address)
        params = urlparse.parse_qsl(parsed.query)
        new_payload = {}
        for x, y in params:
            new_payload[x] = y
        partial_result = get(payload=new_payload, sending_address=next_page_address)
        result.extend(partial_result)
    elif isinstance(response, dict) and "value" not in response:  # condition for when the response is a single item
        if any(response):
            result.append(response)
    return result


def add_result(evaluator, result, field_name="results", failure_type="non_critical_failures"):
    """Adds a result to the specified field, if there is an error it is added to the specified failure type


    :param evaluator: the current evaluator
    :param result: the result to add
    :param field_name: the environment field to which append the result
    :param failure_type: the failure type to which send the result, if it is an error
    """
    if "error" in result:
        evaluator.environment[failure_type].append(result)
    else:
        evaluator.environment[field_name].append(result)


def select_items(evaluator):
    """Remove the selected items that don't match the '--select' conditions
    :param evaluator: the current evaluator
    """
    if bool(evaluator.environment["selected_items"]) and bool(evaluator.args.select):
        for single_item in evaluator.environment["selected_items"].copy():
            matching = selection_parser.select_parser(evaluator.args.select, single_item)
            if not matching:
                evaluator.environment["selected_items"].remove(single_item)
            elif isinstance(matching, dict):
                if "error" in matching:
                    evaluator.environment["selected_items"].remove(single_item)
                    evaluator.environment["non_critical_failures"] += [matching]
        if len(evaluator.environment["selected_items"]) == 0:
            evaluator.environment["critical_failures"] += [f"error: no {evaluator.args.ogc} found "
                                                           f"with select statement conditions"]


def file_iterator(file_name):
    """Creates a new evaluator and uses it to evaluate the commands
    stored in the specified file

    :param file_name: the name of the file
    """
    from evaluator_package.evaluator import EvaluatorClass  # late import for avoiding cross-import problems
    file_evaluator = EvaluatorClass(["-i"], reading_file=True)
    file = open(file_name)
    requests_list = file.readlines()
    for request in requests_list:
        file_evaluator.evaluate(shlex.split(request))
    file.close()


def check_user_defined_arguments(evaluator, all_mandatory_fields, at_least_one_field, needed_additional_argument):
    """Check if the arguments provided by the user are correct"""
    mandatory_fields = all_mandatory_fields
    at_least_one = at_least_one_field
    if not bool(needed_additional_argument):
        return True
    elif not bool(all_mandatory_fields):
        mandatory_fields = []
    elif not bool(at_least_one_field):
        at_least_one = []
    # checking options requiring user-provided values
    for i in needed_additional_argument:
        if evaluator.args.__dict__[i] == ["MISSING_USER_DEFINED_VALUE"] or (not bool(evaluator.args.__dict__[i])\
                                                                            and (
                                                                                    i in mandatory_fields or i in at_least_one or i in needed_additional_argument)):
            help_string = ""
            for j in evaluator.parser._actions:
                if ("--" + i) in j.option_strings:
                    help_string = j.help
                    break
            value = shlex.split(input(f"Missing value for {i}, insert a valid one or 'exit' to exit\n"
                                      f"(help: "
                                      f"{help_string})\n"))
            if value == ["exit"]:
                clear_environment_after_failure(evaluator)
                return False
            else:
                evaluator.args.__dict__[i] = value
    return True


def clear_environment_after_failure(evaluator):
    """Clears the environment keeping the old values of mode and GOST address"""

    evaluator.return_environment = evaluator.environment  # needed as temporary value for the exit function
    temp_address = evaluator.environment["GOST_address"]
    temp_mode = evaluator.environment["mode"]
    evaluator.environment = default_env(GOST_address=temp_address, mode=temp_mode)
