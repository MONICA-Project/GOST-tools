import argparse


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

    parser.add_argument("--sql", help="choose a FILE from which execute a sql-like query",
                        action="store", default=False)

    parser.add_argument("--template", help="choose a template from a file to use as base for --create",
                        action=UserOptionalValue)

    parser.add_argument("--store", help="store the results of command execution in the specified file",
                        action="store", default=False)

    parser.add_argument("-t", "--ogc", "--type",
                        help="select the OGC Model name of the items to process")

    parser.add_argument("-m", "--mode", help="Select an alternative mode of operation."
                                             "Actually available modes:\n"
                                             "- test\n-default")

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
                        "examples:\n--p id <newId> name <newName>\n--p description <newDescription>")

    parser.add_argument("-s", "--select", nargs='*', help="selection of the items from those found with --get,"
                                                          "before any further operation like delete or patch."
                                                          "Chosen items are those in which FIELD "
                                                          "has the selected VALUE. It is usable with " 
                                                          "multiple values at once, starting with 'and/or' depending " 
                                                          "if the user wants ALL fields matching or AT LEAST one"
                                                          "\n(ex: -s id <definedId> name <definedName>)"
                                                          "\n(ex: -s and id <definedId> name <definedName>)"
                                                          "\n(ex: -s or id <definedId> name <definedName>)")

    parser.add_argument("--show", nargs='*', help="select from the results of elaborations"
                                                  "the choosen fields, "
                                                  "usable with multiple values at once "
                                                  "Use 'all' to show all fields "
                                                  "(ex: --show id name)", default=False)

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
    parser.add_argument("--create", action=UserOptionalValue,
                        help="Creates n items of type t in created_files/<type>,"
                        "or in the file defined with 'file <filename>\n"
                        "you can define field values for created records\n"
                        "otherwise default value will be used\n"
                        "(ex: --create num 2 type Sensors file <filename> description new_description)")
    parser.description = "Process user-defined GOST operations"
    return parser


class UserOptionalValue(argparse.Action):
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
