import argparse


def common_commands_parser():
    parser = argparse.ArgumentParser(fromfile_prefix_chars="$")

    parser.add_argument("identifier", help="ID or Name of one or more items to process, "
                                           "or '$' followed by the name of a file with a list of them "
                                           "or 'all' for all the items of chosen type",
                        nargs='*', default=False)

    parser.add_argument("-f", "--file", help="choose a FILE from which to execute a list of commands",
                        action="store", dest="file", default=False)

    parser.add_argument("-t", "--ogc", "--type"
                        , help="OGC Model name of the type of the item to process")

    parser.add_argument("-m", "--mode", help="Select an alternative mode of operation."
                                             "Actually available modes:\n"
                                             "- test\n-default", default=False)

    parser.add_argument("-d", "--delete", help="delete the chosen items",
                        action="store_true")

    parser.add_argument("-i", "--info", help="shows GOST address and operation mode",
                        action="store_true")

    parser.add_argument("-p", "--patch", nargs='*', help="patch the chosen item FIELD with selected VALUE,"
                                                         "usable with multiple values at once "
                                                         "(ex: -p id <newId> name <newName>)")

    parser.add_argument("-s", "--select", nargs='*', help="selection of the items from those found with --get,"
                                                          "before any further operation like delete or patch."
                                                          "Choosen items are those in which FIELD "
                                                          "has the selected VALUE,"
                                                          "usable with multiple values at once "
                                                          "(ex: -s id <definedId> name <definedName>)")

    parser.add_argument("--show", nargs='*', help="select from the results of elaborations"
                                                  "the choosen fields, "
                                                  "usable with multiple values at once "
                                                  "Use 'all' to show all fields "
                                                  "(ex: --show id name)", default=False)

    parser.add_argument("--viewget", nargs='*', help="select from the items found with --get"
                                                  "the selected fields, "
                                                  "usable with multiple values at once."
                                                  "Use 'all' to show all fields "
                                                  "(ex: --viewget id name)", default=False)

    parser.add_argument("-G", "--GOSTaddress", "--address",
                        help="sets a new address (IP and port) for GOST")

    parser.add_argument("--pingconnection", "--connectiontest", "--conntest",
                        help="sends a ping to test the connection", action="store_true")

    parser.add_argument("-g", "--get", help="get the items of the currently "
                                            "selected ogc type,"
                                            "if one or more identifiers are definited,"
                                            "or all the items of seleted type"
                                            "if nothing is defined. "
                                            "The results are saved for successive operations"
                                            "like delete and patch",
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
                                                                   "(ex: --create num 2 type Sensors\n"
                                                                   "description newDesc)")
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
