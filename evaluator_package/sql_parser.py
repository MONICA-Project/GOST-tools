import copy

"""Implemented Grammar:
S    -> (S) S_1 | a_1 S_1 | not (S) S_1
S_1  -> bool S S_1 | epsilon
a_1  -> a | not a
a    -> record_field comp record_field | record_field in record_field | record_field not in record_field

bool -> and | or
comp -> == | != | > | < | >= | <= | <> | gt | lt | gteq |  lteq | diff
"""


def parse(left, right, tokens):
    if not(bool(tokens)):
        return False
    tokenize_parentheses(tokens)
    local_tokens_copy = copy.deepcopy(tokens)  # necessary because the parser removes all the elements from
                                               # tokens list during evaluation
    return S(left, right,local_tokens_copy)


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
    if not(bool(tokens)):
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
    temp_val_1 = get_value(left,right, tokens[0])
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
            return  temp_val_1 < temp_val_2
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
    return "parsing error"


def is_field(token):
    return token in ["name", "description", "encodingType", "location", "properties", "metadata",
                     "definition", "phenomenonTime", "resultTime", "observedArea", "result", "@iot.id",
                     "resultQuality","validTime", "time", "parameters", "feature"]


def is_value(token):
    return not (is_field(token) or token in ["(", ")", "and", "or", "in", "not"])


def tokenize_parentheses(tokens):
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
    if token in l:
        result = l[token]
        return result
    elif token in r:
        result = r[token]
        return result
    else:
        parse_error()




def parse_args(args):
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
    temp_result = []

    for item in entities:
        temp_item = {}
        for key, value in item.items():
            temp_item[f"[{name}]{key}"] = item[key]
        temp_result.append((temp_item))
    return temp_result


def join(left_result, right_result, conditions):
    final_result = []
    for l in left_result:
        comparison = compare(l, right_result, conditions)
        if bool(comparison):
            final_result += comparison
    return final_result


def compare(left_entity, right_results, conditions):
    result = []
    for r in right_results:
        comparison_result = single_compare(left_entity, r, conditions)
        if bool(comparison_result):
            result.append(comparison_result)
    return result


def single_compare(left, right, conditions):
    matching = parse(left, right, conditions)
    if matching:
        return [left, right]
    else:
        return False


def show_filter(result, fields):
    show_result = []
    temp_result_couple = []
    temp_entity = {}
    for couple in result:
        for entity in couple:
            for key in entity:
                if key in fields:
                    temp_entity[key] = entity[key]
            temp_result_couple.append(copy.deepcopy(temp_entity))
            temp_entity = {}
        show_result.append(copy.deepcopy(temp_result_couple))
        temp_result_couple = []
    return show_result

