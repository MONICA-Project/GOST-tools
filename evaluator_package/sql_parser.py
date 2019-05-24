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