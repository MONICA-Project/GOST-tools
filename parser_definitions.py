import argparse
from evaluator_package.evaluator_utilities import is_ogc
from evaluator_package.selection_expression_validator import *
import shlex


def common_commands_parser():
    """The commands common to all parsers in all mode.
    If an argument has a const value of 'MISSING_USER_DEFINED_VALUE', a value will be required to the user
    by 'evaluating conditions decorator' function if the argument is present in the instruction but has no
    value"""

    parser = argparse.ArgumentParser(fromfile_prefix_chars="$")

    parser.add_argument("identifier", help="ID or Name of one or more items to process, "
                                           "or '$' followed by the name of a file with a list of them "
                                           "or 'all' for all the items of chosen type",
                        nargs='*', default=False)

    parser.add_argument("--file", action=UserOptionalValue,
                        help="choose a FILE from which execute a list of commands")

    parser.add_argument("--sql", help="choose a FILE from which execute a sql-like query, or write "
                                      "directly the query",
                        action="store", default=False)

    parser.add_argument("--template", help="choose a template from a file to use as base for --create",
                        action=UserOptionalValue)

    parser.add_argument("--related", help="""gets the entities of ogc_entity_type which shares a datastream with the\n
                        currently selected items, and adds a field "related <ogc type of the previously\n
                        selected items>" to each result\n
                        Accepts select <boolean expression> as additional value to filter the results\n
                        
                        example:\n
                        1 --type Sensors --related Observations\n
                        1 --type Sensor --related Observations select @iot.id > 10\n
                        
                        If the currently selected item is a datastream, found the related items\n
                        
                        example: find all the Observations of the datastreams with @iot.id 10 and 11\n
                        10 11 -t Datastreams --related Observations\n
                        
                        If the currently selected item is a not datastream, and the related command type\n
                        is a datastream, will find all the datastreams related to the selcted item/s\n
                        
                        example: find all the datastreams related to the things with @iot.id 10 and 11\n
                        10 11 -t Things --related Datastreams\n
                        
                        A select condition may be added before the related type\n
                        example: find all the Observations of the datastreams with @iot.id 10 and 11,\n
                        which have a result > 10\n
                        10 11 -t Datastreams --related Observations select result > 10\n""",
                        action=UserOptionalValue)

    parser.add_argument("--store", help="store the results of command execution in the specified file\n",
                        action=CheckValues)

    parser.add_argument("-t", "--ogc", "--type",
                        help="select the OGC Model name of the items to process")

    parser.add_argument("-m", "--mode", help="Select an alternative mode of operation."
                                             "Actually available modes:\n"
                                             "-test\n-default")

    parser.add_argument("-d", "--delete", help="delete the items chosen with get"
                                               "es: -g 15 -t Sensors --delete",
                        action="store_true")

    parser.add_argument("-i", "--info", help="shows the current GOST address and operation mode",
                        action="store_true")

    parser.add_argument("--silent", help="shuts all the screen outputs of evaluation",
                        action="store_true")

    parser.add_argument("-p", "--patch",
                        action=UserOptionalValue,
                        help="patch the chosen item FIELD with selected VALUE,accepts "
                        "multiple values at once\n"
                        "examples:\n--patch id <newId> name <newName>\n--patch description <newDescription>")

    parser.add_argument("-s", "--select", action=CheckValues,
                        help="selection of the items from those found with --get,"
                        "before any further operation like delete or patch."
                        "Chosen items are those in which FIELD "
                        "has the selected VALUE. It is usable with " 
                        "multiple values at once, starting with 'and/or' depending " 
                        "if the user wants ALL fields matching or AT LEAST one"
                        "\n(ex: -s id <definedId> name <definedName>)"
                        "\n(ex: -s and id <definedId> name <definedName>)"
                        "\n(ex: -s or id <definedId> name <definedName>)")

    parser.add_argument("--show", action=CheckValues,
                        help="select from the results of the elaboration the fields, to show\n"
                        "usable with multiple values at once "
                        "(ex: --show id name)")

    parser.add_argument("-G", "--GOSTaddress", "--address",
                        help="sets a new address (IP and port) for GOST")

    parser.add_argument("--pingconnection", "--connectiontest", "--conntest",
                        help="sends a ping to test the connection", action="store_true")

    parser.add_argument("-g", "--get", help="get the items of the currently selected ogc type,if\n"
                        "one or more item identifiers or name are definited,\n"
                        "or all the items of selected type if no id or name\n" 
                        "is provided. The query results are\n"
                        "saved for successive operations like delete or patch",
                                            action="store_true")

    parser.add_argument("--exit", help="exit from the program", action="store_true")

    parser.add_argument("--interactive", help="starts an interactive session, --exit to return to"
                                              "shell", action="store_true")
    parser.add_argument("--post", action=UserOptionalValue,
                        help="posts records from user defined file/s to currently selected OGC type\n"
                        "(ex:'--post <file_name> -t <type>'")

    return parser


def init_default_parser():
    parser = common_commands_parser()
    parser.add_argument("--create", action=CheckValues,
                        help="Creates n items of type t in created_files/<type>,"
                        "or in the file defined with 'file <filename>\n"
                        "you can define field values for created records\n"
                        "otherwise default value will be used\n"
                        "(ex: --create num 2 type Sensors file <filename> description new_description)")
    parser.description = "Process user-defined GOST operations"
    return parser


class UserOptionalValue(argparse.Action):
    """A custom action for all the values which can be initialized both with or without arguments, but in
    the second case a flag 'MISSING_USER_DEFINED_VALUE' will be setted as value"""

    def __init__(self,option_strings,
                 dest=None,
                 nargs="*",
                 default=False,
                 required=False,
                 type=None,
                 metavar=None,
                 help=None):
        super(UserOptionalValue, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            default=default,
            required=required,
            metavar=metavar,
            type=type,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        if not bool(values):
            values = ["MISSING_USER_DEFINED_VALUE"]
        setattr(namespace, self.dest, values)


class CheckValues(argparse.Action):
    """A custom action for all the values which can be initialized both with or without arguments, but in
    the second case the user will be asked to provide one"""

    def __init__(self,option_strings,
                 dest=None,
                 nargs="*",
                 default=False,
                 required=False,
                 type=None,
                 metavar=None,
                 help=None):
        super(CheckValues, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            default=default,
            required=required,
            metavar=metavar,
            type=type,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        if not bool(values):
            check_values(values, self.dest, self.help)
        setattr(namespace, self.dest, values)


def check_values(values, destination, help_message):
    if destination == "create":
        check_create(values)
    elif destination == "select":
        check_select(values)
    else:  # default missing value check
        ask_missing_value(destination, str, f"Missing {destination} value/s, insert one or 'exit' to exit\n"
        f"[help: {help_message}]\n", values)


def check_create(values):
    if "num" not in values:
        ask_missing_value("num", int, "Missing number of items to create, insert one or 'exit' to exit\n", values)

    if "type" not in values:
        ask_missing_value("type", str, "Missing entity type of the items to create,\n "
                                       "choose one or 'exit' to exit\n", values,
                          optional_check_function=is_ogc, optional_value_type_name="ogc entity type")


def ask_missing_value(value_name, value_type, input_request="", values=None,
                      optional_check_function=False, optional_value_type_name=False):
    valid_value = False
    value = input(input_request)
    if value == "exit":
        exit(0)
    elif optional_check_function:
        if optional_check_function(value):
            values += [str(value)]
            valid_value = True
    elif is_of_type(value, value_type):
        values += [str(value)]
        valid_value = True

    if not valid_value:
        while not valid_value:
            if not optional_value_type_name:
                value = input(f"Invalid input, needed a {value_type}\n "
                          f"Insert a valid input or 'exit' to exit\n")
            else:
                value = input(f"Invalid input, needed a {optional_value_type_name}\n "
                              f"Insert a valid input or 'exit' to exit\n")

            if value == "exit":
                exit(0)
            elif optional_check_function:
                if optional_check_function(value):
                    values += [str(value)]
                    valid_value = True
            elif is_of_type(value, value_type):
                values += [str(value)]
                valid_value = True
    pass


def check_select(values):
    valid_expression = select_parser_validator(values)
    if not valid_expression:

        while not valid_expression:
            user_expression = input("Error: invalid select expression, insert a valid one or 'exit' to exit\n")
            if user_expression == "exit":
                exit(0)
            valid_expression = select_parser_validator(shlex.split(user_expression))

        values.clear()
        values += shlex.split(user_expression)


def is_of_type(object_string, type):
    try:
        type(object_string)
        return True
    except ValueError:
        return False

