from ogc_utility import *
import pprint
from json import JSONDecoder, JSONDecodeError
import re
from creation_utilities import create_records_file
from evaluator_package.environments import default_env
import copy
from . import evaluating_conditions_decorator as conditions
from . import selection_parser
from . import exceptions as exception
from . import sql_mode as sql


@conditions.needed_fields(at_least_one_field=[], critical_failures_resistant=False)
def connection_test(evaluator):
    """Tests the connection on the currently defined GOST address"""

    if not connection_config.test_connection(evaluator.environment.GOST_address, False):
        print("Network error, failed connection")
        evaluator.environment["critical_failure"].append("failed connection "
                                                         "to " + evaluator.environment["GOST_address"][:-5])
    else:
        print(f"current GOST address: {evaluator.environment.GOST_address}\n'--address <ip:port>' to change")


@conditions.needed_fields(all_mandatory_fields=["delete"], critical_failures_resistant=False,
                          needed_ogc=True, needed_items=True)
def delete(evaluator):
    """Delete from GOST db the selected items:
    before deleting asks user for confirmation"""

    if evaluator.environment["selected_items"]:  # deleting selected items
        warning_message = f"You are going to delete the {evaluator.args.ogc} " \
            f"with the following name (if available) and id:\n"   # creation of warning message
        for x in evaluator.environment["selected_items"]:
            try:
                if "error" in x:
                    pass
                elif "@iot.id" in x:
                    if "name" in x:
                        warning_message += f"id = {str(x['@iot.id'])} - name = {str(x['name'])}\n"
                    else:
                        warning_message += f"id = {str(x['@iot.id'])}\n"
            except AttributeError as attr:
                print("missing" + attr)
                pass
        for x in evaluator.environment["non_critical_failures"]:
            if "error" in x:
                print(x["error"]["message"])

        proceed = input(warning_message + "\nProceed?(y/N)")

        if proceed == "y":  # elimination of items
            if bool(evaluator.environment["selected_items"]):
                for x in evaluator.environment["selected_items"]:
                    try:
                        if "error" in x:
                            evaluator.environment["non_critical_failures"].append(x["error"])
                        elif "@iot.id" in x:
                            result = delete_item(x.get("@iot.id"), evaluator.args.ogc, evaluator.environment)
                            conditions.add_result(evaluator, result, "results")
                    except AttributeError as attr:
                        print("missing" + attr)
                        pass
                evaluator.environment["selected_items"] = []
        else:
            evaluator.environment["selected_items"] = []
            print("Aborted deletion")
    else:
        print("trying to delete but no item defined or found")


@conditions.needed_fields(critical_failures_resistant=True)
def exit_function(evaluator):
    """exits at the end of the current evaluation (not working if is reading a file): used for the first evaluation"""

    if evaluator.reading_file:
        pass
    elif evaluator.args.exit:
        raise exception.PassEnvironmentException(exit_interactive_mode=True)
        exit(0)
    else:
        raise exception.PassEnvironmentException(evaluator.return_environment)


@conditions.needed_fields(at_least_one_field=[], critical_failures_resistant=False)
def execute_and_exit(evaluator):
    """exits at the end of the current evaluation: used for the evaluations beyond the first"""

    if evaluator.args.interactive:
        print("Entering interactive mode: --exit to return to shell")
    elif evaluator.reading_file:
        pass
    else:
        raise exception.PassEnvironmentException(evaluator.return_environment)


@conditions.needed_fields(at_least_one_field=["info"], all_mandatory_fields=[],
                          critical_failures_resistant=True)
def get_info(evaluator):
    """Prints the following informations about the current evaluator:
    -operation mode
    -GOST address
    """

    if evaluator.environment["mode"]:
        print("Mode : " + str(evaluator.environment["mode"]))
    if evaluator.environment["GOST_address"]:
        print("Address : " + evaluator.environment["GOST_address"])


# the items are retrieved  in the decorator, thanks to the needed_items flag
@conditions.needed_fields(at_least_one_field=["get"], needed_ogc=True,
                          critical_failures_resistant=False, needed_items=True)
def get_command_line(evaluator):
    """Gets the items from GOST, used if get or identifier are defined"""
    pass


@conditions.needed_fields(all_mandatory_fields=["patch"],
                          needed_additional_argument=["patch"],
                          critical_failures_resistant=False,
                          needed_ogc=True, needed_items=True)
def patch(evaluator):
    """Patches the selected fields of the selected items with the selected values
    """
    patches = args_to_dict(evaluator.args.patch)
    if bool(evaluator.environment["selected_items"]):
        for x in evaluator.environment["selected_items"]:
            if evaluator.environment["selected_items"]:  # patching selected items
                warning_message = f"You are going to patch the {evaluator.args.ogc} " \
                    f"with the following name (if available) and id:\n"  # creation of warning message
                for x in evaluator.environment["selected_items"]:
                    try:
                        if "error" in x:
                            pass
                        elif "@iot.id" in x:
                            if "name" in x:
                                warning_message += f"id = {str(x['@iot.id'])} name = {str(x['name'])} :\n"
                            else:
                                warning_message += f"id = {str(x['@iot.id'])} :\n"
                        patches_temp_copy = copy.deepcopy(patches)
                        for key in patches:
                            if key not in x:
                                wrong_key = key_warning(patches_temp_copy, x, key, key)
                                if wrong_key in ["ignore", "changed_name"]:
                                    pass
                                elif wrong_key == "exit":
                                    exit(0)
                        patches = copy.deepcopy(patches_temp_copy)

                        for key in patches:
                            if key in x:
                                warning_message += f" Patching {key} from {x[key]} to {patches[key]}\n"

                    except AttributeError as attr:
                        print("missing" + attr)
                        pass
                for x in evaluator.environment["non_critical_failures"]:
                    if "error" in x:
                        print(x["error"]["message"])

                proceed = input(warning_message + "\nProceed?(y/N)")

                if proceed == "y":  # elimination of items
                    if bool(evaluator.environment["selected_items"]):
                        for x in evaluator.environment["selected_items"]:
                            try:
                                if "error" in x:
                                    evaluator.environment["non_critical_failures"].append(x["error"])
                                elif "@iot.id" in x:
                                    for key in patches:  # checking if all the patches are for valid entity attributes
                                        if key not in x.keys():
                                            evaluator.environment["critical_failures"].append(
                                                {"error": f"invalid attribute name: {key}"})
                                            return False
                                    result = patch_item(patches, str(x.get("@iot.id")), evaluator.args.ogc,
                                                        evaluator.environment)
                                    conditions.add_result(evaluator, result, "results")
                            except AttributeError as attr:
                                print("missing" + attr)
                                pass
                        evaluator.environment["selected_items"] = []
                else:
                    evaluator.environment["selected_items"] = []
                    print("Aborted patching")
    else:
        print("trying to patch but no item defined or found")


@conditions.needed_fields(at_least_one_field=["pingconnection"], critical_failures_resistant=True)
def ping(evaluator):
    """Tests the connection, used for when id is explicitly asked by the user"""

    if evaluator.environment["GOST_address"]:
        connection_config.test_connection(evaluator.environment["GOST_address"][:-5], verbose=True)
    else:
        evaluator.environment["non_critical_failures"].append("GOST address undefined, ping not possible")


@conditions.needed_fields(at_least_one_field=["post"], needed_additional_argument=["post"],
                          critical_failures_resistant=False,
                          needed_ogc=True)
def post(evaluator):
    """Reads the records (one per line) from a file and posts them to the selected entity type"""

    for file in evaluator.args.post:
        with open(file) as json_file:
            NOT_WHITESPACE = re.compile(r'[^\s]')

            def decode_stacked(document, pos=0, decoder=JSONDecoder()):
                while True:
                    match = NOT_WHITESPACE.search(document, pos)
                    if not match:
                        return
                    pos = match.start()

                    try:
                        obj, pos = decoder.raw_decode(document, pos)
                    except JSONDecodeError:
                        raise
                    yield obj

            for obj in decode_stacked(json_file.read()):
                result = add_item(obj, evaluator.args.ogc)
                json_result = json.loads((result.data).decode('utf-8'))
                conditions.add_result(evaluator, json_result, "results")


@conditions.needed_fields(at_least_one_field=["related"], needed_additional_argument=["related"], needed_items=True)
def related_items(evaluator):
    """Find the items of the choosen type which share a datastream with the currently selected item
    If the currently selected item is a datastream, will be found the items of the choosen type related to
    that datastream"""
    result = []

    if evaluator.args.ogc == "Datastreams":
        if evaluator.args.related[0] == "Datastreams":
            evaluator.environment["critical_failure"].append({"error": "trying to found "
                                                                       "Datastreams related to Datastreams"})
        else:
            for item in evaluator.environment["selected_items"]:
                result += get_entities_from_datastream(item, evaluator.args.related[0],
                                                       evaluator.environment["GOST_address"])
            evaluator.environment["selected_items"] = result

    else:
        if evaluator.args.related[0] == "Datastreams":
            for item in evaluator.environment["selected_items"]:
                result += related_datastreams(item['@iot.id'], evaluator.args.ogc,
                                              evaluator.environment["GOST_address"])

        else:
            for item in evaluator.environment["selected_items"]:
                result += find_related(item, evaluator.args.ogc, evaluator.args.related[0],
                                       evaluator.environment["GOST_address"])
        evaluator.environment["selected_items"] = result

    # checks on the query result the conditions given to --related as argument
    # (es: --related Sensors select "turin" in name)

    temp_list = []

    if len(evaluator.args.related) > 1 and evaluator.args.related[1] == "select":
        # there are selection filters
        # inside "related" command
        selection_rules = evaluator.args.related[2:]
        for item in evaluator.environment["selected_items"]:
            matching = selection_parser.select_parser(selection_rules, item)
            if not matching:
                pass
            elif isinstance(matching, dict):
                if "error" in matching:
                    evaluator.environment["selected_items"].remove(item)
                    evaluator.environment["non_critical_failures"] += [matching]
            else:
                temp_list.append(item)
        evaluator.environment["selected_items"] = temp_list

    evaluator.args.ogc = evaluator.args.related[0]  # change the selected items type to the result type
        # for future operations


@conditions.needed_fields(at_least_one_field=["select"], critical_failures_resistant=False, needed_items=True)
def select_items_command(evaluator):
    """Selects from the selected_items all the items matching with the rules
    defined in evaluator.args.select and removes the others"""
    conditions.select_items(evaluator)


@conditions.needed_fields(at_least_one_field=["show"], critical_failures_resistant=False,
                          needed_additional_argument=["show"])
def select_result_fields(evaluator):
    """Selects which fields of the record in result will be showed.
    If get is defined but there is no result, all the getted items will be
    showed"""
    if evaluator.args.show == "silent":
        return False
    elif not bool(evaluator.environment["results"]) and bool(evaluator.environment["selected_items"]):
        # if at the end of the execution of the command there are some selected items, they are added
        # to the result
        evaluator.environment["results"] = copy.deepcopy(evaluator.environment["selected_items"])
        evaluator.environment["selected_items"] = []

    if evaluator.args.show:
        for x in evaluator.environment["results"]:
            for field in x.copy():
                if field not in evaluator.args.show:
                    x.pop(field, None)
            for show_field in evaluator.args.show:
                if show_field not in x.copy():
                    x[show_field] = "ERROR: field not available"


@conditions.needed_fields(no_fields=["GOSTaddress"],at_least_one_field=[],
                          all_mandatory_fields=[], critical_failures_resistant=False)
def saved_address(evaluator):
    """Checks if there is a saved address, and tries to connect to it.
    This method is intended only for the first evaluation of the session"""

    evaluator.environment["GOST_address"] = connection_config.set_GOST_address()
    if not evaluator.environment["GOST_address"]:
        evaluator.environment["critical_failures"].append("error: GOST address missing or not working")


@conditions.needed_fields(at_least_one_field=[], critical_failures_resistant=True, no_fields=["silent"])
def show_failures(evaluator):
    """Shows the failures occurred during evaluation"""

    if evaluator.environment["critical_failures"]:
        for x in evaluator.environment["critical_failures"]:
            print(x)
        print("Found "+ str(len(evaluator.environment["critical_failures"])) + " critical_failures\n")

    if evaluator.environment["non_critical_failures"]:
        for x in evaluator.environment["non_critical_failures"]:
            print(x)
        print("Found " + str(len(evaluator.environment["non_critical_failures"])) + " non_critical_failures\n")


@conditions.needed_fields(at_least_one_field=["sql"], needed_additional_argument=["sql"])
def sql_evaluate(evaluator):
    """Evaluate a sql-like query stored in the file provided by the user"""
    evaluator.environment["selected_items"] = sql.evaluate(evaluator)


@conditions.needed_fields(critical_failures_resistant=False, no_fields=["silent"])
def show_results(evaluator):
    """Shows the results of evaluation"""

    if bool(evaluator.environment["selected_items"]):  # final check for seleced items not sent to result
        evaluator.environment["results"] = copy.deepcopy(evaluator.environment["selected_items"])
    if evaluator.environment["results"]:
        pp = pprint.PrettyPrinter(indent=4)
        for x in evaluator.environment["results"]:
            pp.pprint(x)
        print(str(len(evaluator.environment["results"])) + " results found\n")


@conditions.needed_fields(at_least_one_field=["store"], needed_items=True)
def store(evaluator):
    """Stores the current command results in the file defined by user in args.store"""
    file = open(evaluator.args.store[0], "w")
    file.write(json.dumps(evaluator.environment["results"]))


@conditions.needed_fields(all_mandatory_fields=["template"],
                          needed_additional_argument=["template", "create"],
                          critical_failures_resistant=False)
def template(evaluator):
    """Create records filling the fields with a template defined in the user-provided file"""
    print(evaluator.args.template)
    template_file = open(evaluator.args.template[0])
    template_lines = template_file.readlines()
    template_string = ""
    for line in template_lines:
        template_string += line + " "
    template_dict = json.loads(template_string)
    creation_values = args_to_dict(evaluator.args.create)

    for key in creation_values:
        template_dict[key] = creation_values[key]

    result = create_records_file(template_dict)
    if result["errors"]:
        evaluator.environment["non_critical_failures"] += result["errors"]
    if evaluator.args.show:
        if result["created_name_list"]:
            evaluator.environment["results"] += result["created_name_list"]


@conditions.needed_fields(at_least_one_field=["GOSTaddress"], critical_failures_resistant=False)
def user_defined_address(evaluator, verbose=True):
    """If the user has defined a GOST address, checks if it is possible to reach it.
    If it possible, sets the GOST address to the new address, otherwise asks the user if he
    wants to select a different address or wants to keep the non working address"""

    working_conn = connection_config.test_connection((evaluator.args.GOSTaddress)[:-5])
    if working_conn:
        valid_conn = connection_config.set_GOST_address(evaluator.args.GOSTaddress)
        evaluator.environment["GOST_address"] = valid_conn
    else:
        warning_message = f"The selected GOST address is not working, " \
            f"do you want to set it as your address or want to change it?\n" \
            f"'y' to set the currently provided address\n'ch' to set a new address\n" \
            f"'n' to mantain the old address:\n"  # creation of warning message
        proceed = input(warning_message)
        if proceed == "y":
            valid_conn = connection_config.set_GOST_address(evaluator.args.GOSTaddress)
            evaluator.environment["GOST_address"] = valid_conn
        elif proceed == "ch":
            new_address = input("Insert new address:\n")
            evaluator.args.GOSTaddress = new_address
            user_defined_address(evaluator)

        else:
            evaluator.environment["GOST_address"] = connection_config.set_GOST_address()
            if not evaluator.environment["GOST_address"]:
                evaluator.environment["critical_failures"].append("error: GOST address not defined")


@conditions.needed_fields(no_fields=["template"], at_least_one_field=["create"],
                          needed_additional_argument=["create"],
                          critical_failures_resistant=False)
def create_records(evaluator):
    """create records to store in a file"""
    create(evaluator)


@conditions.needed_fields(at_least_one_field=["file"], needed_additional_argument=["file"],
                          critical_failures_resistant=False)
def exec_file(evaluator):
    """Executes a list of commands stored in a file"""
    # TODO recursion control
    if evaluator.args.file:
        conditions.file_iterator(list_to_string(evaluator.args.file))


def create(evaluator):
    """Create records in a file"""

    result = create_records_file(args_to_dict(evaluator.args.create))
    if result["errors"]:
        evaluator.environment["non_critical_failures"] += result["errors"]
    if evaluator.args.show:
        if result["created_name_list"]:
            evaluator.environment["results"] += result["created_name_list"]


def clear_environment(evaluator):
    """Clears the environment keeping the old values of mode and GOST address"""

    evaluator.return_environment = evaluator.environment  # needed as temporary value for the exit function
    temp_address = evaluator.environment["GOST_address"]
    temp_mode = evaluator.environment["mode"]
    evaluator.environment = default_env(GOST_address=temp_address, mode=temp_mode)


def find_related(item, item_type, related_type, address):
    """Returns a list of the entities of related_type which share a datastream with item"""
    datastreams = related_datastreams(item['@iot.id'], item_type, address)
    result = []
    for related_datastream in datastreams:
        related_result = get_entities_from_datastream(related_datastream, related_type, address)
        if bool(related_result):
            result += related_result
    result = remove_duplicates_by_key(result, "@iot.id")
    for i in result:
        i[f"related {item_type} id"] = item["@iot.id"]
    return result


def related_datastreams(id, type, base_address):
    """Returns a list of all the datastreams related with the item with id = id and type = type"""

    related_datastreams_address = f"{base_address}/{type}({id})/Datastreams"
    result = get_all(sending_address=related_datastreams_address)
    if not bool(result):
        related_datastreams_address = f"{base_address}/{type}({id})/Datastream"  # for some type of entities
                                                                        # like Observations GOST remove the final 's'
        result = get_all(sending_address=related_datastreams_address)
    return result


def match(first_list, second_list, attribute_name):
    """Compares two lists and returns true if in both there is at least one element which
    has the same value for the attribute 'attribute_name' """
    for i in first_list:
        for j in second_list:
            if i[attribute_name] == j[attribute_name]:
                return True
    return False


def get_entities_from_datastream(datastream, entity_type, base_address):
    """Returns a list of all the entities of type entity_type related to datastream"""
    address = f"{base_address}/Datastreams({datastream['@iot.id']})/{entity_type}"
    result = get_all(sending_address=address)
    if not bool(result):
        address = address[:-1]  # for some type if entities the removal of final -s is needed
        result = get_all(sending_address=address)

    return result


def remove_duplicates_by_key(list_to_clear, key_name):
    """Removes from list_to_clear, a list of dictionaries, all the elements which have 'key_name' and  key values
    equals, lefting only one"""
    result_list = []
    key_values_list = []
    for i in list_to_clear:
        if str(i[key_name]) in key_values_list:
            pass
        else:
            key_values_list.append(str(i[key_name]))
            result_list.append(i)
    return result_list


def key_warning(patches_dictionary, item, key, originally_wrong_key = False):
    """It warns if the key the user is trying to patch doesn't exist"""
    key_user_warning = input(f"You are trying to patch the field {key} but it does not exists,\n "
                             f"do you want to:\n "
                             f"change field name [type 'name']\n"
                             f"continue with patching ignoring that field [type 'ignore']\n"
                             f"exit the patching operation [type 'exit']\n")
    if key_user_warning in "name":
        available_fields = "["
        for item_key in item:  # creating a preview of the available fields for the user
            if item_key not in patches_dictionary:  # checking if the field is not already patched
                available_fields += item_key + "\n"
        available_fields += "]"

        name_warning = input(f"Select a new value for the field name or 'exit' to exit\n"
                             f"available fields:\n" + available_fields + "\n")
        if name_warning in "exit":
            return "exit"
        else:
            if name_warning in item:
                if originally_wrong_key:
                    key = originally_wrong_key
                patches_dictionary[name_warning] = copy.deepcopy(patches_dictionary[key])
                patches_dictionary.pop(key, None)
                return "name_changed"
            else:
                result = key_warning(patches_dictionary, item, name_warning, originally_wrong_key)
                if result == "exit":
                    return "exit"
                elif result == "ignore":
                    return "ignore"
                elif result == "name_changed":
                    return "name_changed"

    elif key_user_warning in "ignore":
        patches_dictionary.pop(key, None)
        return "ignore"
    elif key_user_warning in "exit":
        return "exit"
    else:
        return "Insert a valid option\n" + key_warning(patches_dictionary, item, key_user_warning, originally_wrong_key)


def list_to_string(list):
    """Transform a list to string"""
    result = ""
    for i in list:
        result += i
    return result