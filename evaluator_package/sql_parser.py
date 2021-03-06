import copy
from evaluator_package.evaluating_conditions_decorator import get


"""Implemented Grammar:
S    -> (S) S_1 | a_1 S_1 | not (S) S_1
S_1  -> bool S S_1 | epsilon
a_1  -> a | not a
a    -> record_field comp record_field | record_field in record_field | record_field not in record_field

bool -> and | or
comp -> == | != | > | < | >= | <= | <> | gt | lt | gteq |  lteq | diff
"""

"""Methods S, S_1, a_1, a, are used to evaluates the espression"""


def parse(left, right, tokens):
    """Call the methods for the parsification of the sql expression"""
    if not (bool(tokens)):
        return False
    tokenize_parentheses(tokens)
    local_tokens_copy = copy.deepcopy(tokens)  # necessary because the parser removes all the elements from
    # tokens list during evaluation
    return S(left, right, local_tokens_copy)


def S(left, right, tokens):
    if tokens[0] == "(":
        tokens.pop(0)
        temp_result = S(left, right, tokens)
        if tokens[0] == ")":
            tokens.pop(0)
            return S_1(left, right, tokens, temp_result)
        else:
            return parse_error()
    elif tokens[0] == "not":
        tokens.pop(0)
        if tokens[0] == "(":
            tokens.pop(0)
            temp_result = S(left, right, tokens)
            if tokens[0] == ")":
                tokens.pop(0)
                return not (S_1(left, right, tokens, temp_result))
            else:
                return parse_error()
    else:
        temp_result = a_1(left, right, tokens)
        return S_1(left, right, tokens, temp_result)


def S_1(left, right, tokens, previous_result):
    if not (bool(tokens)):
        return previous_result

    elif tokens[0] == "and" or tokens[0] == "or":
        temp_bool = tokens[0]
        tokens.pop(0)
        temp_result = S(left, right, tokens)
        if temp_bool == "and":
            temp_result = previous_result and temp_result
        elif temp_bool == "or":
            temp_result = previous_result or temp_result
        return S_1(left, right, tokens, temp_result)
    else:
        return previous_result


def a_1(left, right, tokens):
    if tokens[0] == "not":
        tokens.pop(0)
        return not a(left, right, tokens)
    else:
        return a(left, right, tokens)


def a(left, right, tokens):
    temp_val_1 = get_value(left, right, tokens[0])
    tokens.pop(0)
    comparator = []
    comparator.append(tokens[0])
    tokens.pop(0)

    if comparator[0] == "not":
        comparator.append(tokens[0])
        tokens.pop(0)

    temp_val_2 = get_value(left, right, tokens[0])
    tokens.pop(0)

    if comparator[0] == "not":
        if comparator[1] == "in":
            return not (temp_val_1 in temp_val_2)
        else:
            return parse_error()
    elif comparator[0] == "in":
        return temp_val_1 in temp_val_2

    elif comparator[0] == "==":
        return temp_val_1 == temp_val_2

    elif comparator[0] == "!=":
        return temp_val_1 != temp_val_2

    elif comparator[0] == "<" or comparator[0] == "lt":
        return temp_val_1 < temp_val_2
    elif comparator[0] == "<=" or comparator[0] == "lteq":
        return temp_val_1 <= temp_val_2
    elif comparator[0] == ">" or comparator[0] == "gt":
        return temp_val_1 > temp_val_2
    elif comparator[0] == ">=" or comparator[0] == "gteq":
        return temp_val_1 >= temp_val_2
    elif comparator[0] == "<>" or comparator[0] == "diff":
        return not (temp_val_1 == temp_val_2)
    else:
        return parse_error()


def parse_error():
    """Return "parsing error" """
    return "parsing error"


def is_field(token):
    """Checks if the token is a valid ogc type field"""
    return token in ["name", "description", "encodingType", "location", "properties", "metadata",
                     "definition", "phenomenonTime", "resultTime", "observedArea", "result", "@iot.id",
                     "resultQuality", "validTime", "time", "parameters", "feature"]


def is_value(token):
    """Checks if the token is a value"""
    return not (is_field(token) or token in ["(", ")", "and", "or", "in", "not"])


def tokenize_parentheses(tokens):
    """Finds non parsed parentheses in tokens"""
    for index, token in enumerate(tokens):
        if ("(" in token or ")" in token) and len(token) > 1:
            parenthesis_index = token.find("(")
            parenthesis = "("
            if parenthesis_index < 0:
                parenthesis_index = token.find(")")
                parenthesis = ")"
            left_side = token[:parenthesis_index]
            right_side = token[parenthesis_index + 1:]

            del tokens[index]
            if bool(left_side):
                tokens.insert(index, left_side)
                index += 1
            tokens.insert(index, parenthesis)
            if bool(right_side):
                index += 1
                tokens.insert(index, right_side)


def get_value(l, r, token):
    """Return the value if it is in l or r, error otherwise"""
    if token in l:
        result = l[token]
        return result
    elif token in r:
        result = r[token]
        return result
    else:
        parse_error()


def parse_args(args):
    """To parsify the command provided by the user on command line"""
    left_command_args = copy.deepcopy(args[0: args.index("as")])
    args = args[args.index("as") + 1:]
    left_name = args[0]

    right_command_args = copy.deepcopy(args[args.index("join") + 1: args.index("as")])
    args = args[args.index("as") + 1:]
    right_name = args[0]

    args = args[args.index("on") + 1:]
    conditions = args[0: args.index("show")]
    show = args[args.index("show") + 1:]
    return {"left_side": left_command_args, "right_side": right_command_args,
            "left_name": left_name, "right_name": right_name,
            "join_conditions": conditions, "show": show}


def append_name_to_key(entities, name):
    """To append value to corrispondent key"""
    temp_result = []

    for item in entities:
        temp_item = {}
        for key, value in item.items():
            temp_item[f"[{name}]{key}"] = item[key]
        temp_result.append(temp_item)
    return temp_result


def join(left_result, right_result, conditions, left_name, right_name):
    """It join the 'left_result' with 'right_result'"""

    final_result = dict()
    if any("@iot.navigationLink" in c for c in conditions):
        if "@iot.navigationLink" in conditions[0]:
            index = 0
        else:
            index = 2

        if left_name in conditions[index]:
            result = left_result
            opposite = right_result
        else:
            result = right_result
            opposite = left_result
            right_name = left_name

        for l in result:
            address = l[conditions[index]]
            left = get(sending_address=address)
            if type(left) != list:
                return left
            i = 0
            for l_result in left:
                for r in opposite:
                    partial_result = dict()
                    if l_result["@iot.selfLink"] == r["[" + right_name + "]" + "@iot.selfLink"]:
                        partial_result.update(l)
                        partial_result.update(r)
                        final_result[i] = partial_result
                    i += 1
    return final_result


def compare(left_entity, right_results, conditions):
    """Compare 'left_entity' with the 'right_results'"""
    result = []
    for r in right_results:
        comparison_result = single_compare(left_entity, r, conditions)
        if bool(comparison_result):
            result.append(comparison_result)
    return result


def single_compare(left, right, conditions):
    """Compare a single element"""
    matching = parse(left, right, conditions)
    if matching:
        return [left, right]
    else:
        return False


def show_filter(result, fields):
    """Return the corrispondent value to a key passed on the argument"""
    temp_result = dict()
    i = 0
    for f in fields:
        if f == "all" or f == "*":
            return result
    for couple in result.values():
        temp_entity = dict()
        for entity in couple:
            if entity in fields:
                temp_entity[entity] = couple[entity]
        temp_result[i] = temp_entity
        i += 1
    return temp_result
