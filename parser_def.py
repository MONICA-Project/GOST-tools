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

    parser.add_argument("-s", "--select", nargs='*', help="select_items from the items found with --get"
                                                                "those in which FIELD has the selected VALUE,"
                                                                "usable with multiple values at once "
                                                                "(ex: -s id <newId> name <newName>)")

    parser.add_argument("--fields", "--show", nargs='*', help="select from the items found with --get"
                                                              "the selected fields, "
                                                              "usable with multiple values at once "
                                                              "(ex: --field id name)")

    parser.add_argument("-G", "--GOSTaddress", "--address",
                        help="sets a new address (IP and port) for GOST")

    parser.add_argument("--pingconnection", "--connectiontest", "--conntest",
                        help="sends a ping to test the connection", action="store_true")

    parser.add_argument("-g", "--get", help="shows the IDs of the items of the currently "
                                            "selected ogc type,"
                                            "by matching attributes\n"
                                            "es('-g owner <name> description <desc>'.\n"
                                            'Otherwise, if an identifier is definited, shows\n'
                                            'the selected values of the item'
                        , action="store_true")

    parser.add_argument("--exit", help="exit from the program", action="store_true")

    parser.add_argument("--interactive", help="starts an interactive session, --exit to return to"
                                              "shell", action="store_true")
    parser.add_argument("--post", nargs='*', help="posts records from user defined file/s to"
                                                  "currently selected OGC type"
                        , default=False)

    parser.add_argument("--load", nargs='*', help="loads records from file"

                        , default=False)

    parser.add_argument("--create", nargs='*', default=False, help="Creates n items of type t "
                                                                   "in created_files/<type>,"
                                                                   "or in the file defined with 'file <filename>\n"
                                                                   "you can define field values for created records\n"
                                                                   "otherwise default value will be used"
                                                                   "(ex: --create num 2 type Sensors\n"
                                                                   "description newDesc)")
    return parser


def init_default_parser():
    parser = common_commands_parser()
    parser.description = "Process user-defined GOST operations"
    return parser


def init_test_parser():
    parser = common_commands_parser()
    parser.description = "Process user-defined testing oriented GOST operations"

    parser.add_argument("--session", help="with 'start' argument "
                                          "starts a test session, and all created items will be"
                                          "saved in an env variable. With 'clear' all those items will be"
                                          "deleted"
                                           ,
                        default=False)
    parser.add_argument("--clear_session", help="delete all the records created from the beginning of "
                                                "current test session",
                        action="store_true")

    return parser
