import argparse


def common_commands_parser():
    parser = argparse.ArgumentParser(fromfile_prefix_chars="$")

    parser.add_argument("identifier", help="ID or Name of one or more items to process, "
                                           "or '$' followed by the name of a file with a list of them "
                                           "or 'all' for all the items of chosen type",
                        nargs='*', default=False)

    parser.add_argument("--execute", help="choose a FILE from which execute a list of commands",
                        action="store", default=False)

    parser.add_argument("--sql", help="choose a FILE from which execute a sql-like query",
                        action="store", default=False)

    parser.add_argument("--template", help="choose a template from a file to use as base for --create",
                        action="store", default=False)

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

    parser.add_argument("-p", "--patch", nargs='*', help="patch the choosen item FIELD with selected VALUE,accepts "
                                                         "multiple values at once"
                                                          "examples:\n--p id <newId> name <newName>"
                                                          "\n--p description <newDescription>")

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
    parser.add_argument("--post", nargs='*', help="posts records from user defined file/s to"
                                                  "currently selected OGC type"
                                                  "es('--post <file_name> -t <type>'"
                        , default=False)

    return parser


def init_default_parser():
    parser = common_commands_parser()
    parser.add_argument("--create", nargs='*', default=False, help="Creates n items of type t "
                                                                   "in created_files/<type>,"
                                                                   "or in the file defined with 'file <filename>\n"
                                                                   "you can define field values for created records\n"
                                                                   "otherwise default value will be used"
                                                                   "(ex: --create num 2 description new_description"
                                                                   " --type Sensors\n)")
    parser.description = "Process user-defined GOST operations"
    return parser


def init_test_parser():
    parser = common_commands_parser()
    parser.description = "Process user-defined testing oriented GOST operations"
    parser.add_argument("--session", help="with 'start' argument "
                                          "starts a test session, and all created items will be"
                                          "saved in an env variable and in a file with the name of "
                                          "ogc_type in the folder"
                                          "test_files. With 'clear' or  changing"
                                          "the mode all those items will be"
                                          "deleted", default=False)

    parser.add_argument("--create", nargs='*', default=False, help="Creates n items of type t "
                                                                   "test_files/<type>,"
                                                                   "you can define field values for created records\n"
                                                                   "otherwise default value will be used"
                                                                   "(ex: --create num 2 type Sensors\n"
                                                                   "description newDesc)")
    return parser
