import copy

"""Implemented Grammar:
S    -> (S) S_1 | a_1 S_1 | not (S) S_1 | epsilon
S_1  -> bool S S_1 | epsilon
bool -> and | or
a_1  -> a | not a
a    -> record_field comp value | value in record_field | value not in field
comp -> == | != | > | < | >= | <=
"""

def select_parser(tokens, record = None):
    if not(bool(tokens)):
        return False
    local_tokens_copy = copy.deepcopy(tokens)  # necessary because the parser removes all the elements from
                                               # tokens list during evaluation
    return S(local_tokens_copy, record)


def S(tokens, record=None):
    if tokens[0] == "(":
        tokens.pop(0)
        temp_result = S(tokens, record)
        if tokens[0] == ")":
            tokens.pop(0)
            return S_1(tokens, temp_result, record)
        else:
            return parse_error()
    elif tokens[0] == "not":
        tokens.pop(0)
        if tokens[0] == "(":
            tokens.pop(0)
            temp_result = S(tokens, record)
            if tokens[0] == ")":
                tokens.pop(0)
                return not (S_1(tokens, temp_result, record))
            else:
                return parse_error()

    elif is_field(tokens[0]) or is_value(tokens[0]) or tokens[0] == "not":
        temp_result = a_1(tokens, record)
        return S_1(tokens, temp_result, record)

    else:
        return parse_error()


def S_1(tokens, previous_result, record = None):
    if not(bool(tokens)):
        return previous_result

    elif tokens[0] == "and" or tokens[0] == "or":
        temp_bool = tokens[0]
        tokens.pop(0)
        temp_result = S(tokens, record)
        if temp_bool == "and":
            temp_result = previous_result and temp_result
        elif temp_bool == "or":
            temp_result = previous_result or temp_result
        return S_1(tokens, temp_result, record)
    else:
        return previous_result


def a_1(tokens, record = None):
    if tokens[0] == "not":
        tokens.pop(0)
        return not a(tokens, record)
    else:
        return a(tokens, record)


def a(tokens, record):
    if is_value(tokens[0]):
        temp_val = tokens[0]
        tokens.pop(0)
        if tokens[0] == "not":
            tokens.pop(0)
            if tokens[0] == "in":
                tokens.pop(0)
                temp_field = record[tokens[0]]
                tokens.pop(0)
                return not (temp_val in temp_field)
            else:
                return parse_error()
        elif tokens[0] == "in":
            tokens.pop(0)
            temp_field = record[tokens[0]]
            tokens.pop(0)
            return temp_val in temp_field

    elif is_field(tokens[0]):
        temp_field = record[tokens[0]]
        tokens.pop(0)
        if tokens[0] == "==":
            tokens.pop(0)
            temp_val = tokens[0]
            tokens.pop(0)
            if isinstance(temp_field, int):  # necessary for checking @iot.id
                temp_val = int(temp_val)
            return temp_val == temp_field
        elif tokens[0] == "!=":
            tokens.pop(0)
            temp_val = tokens[0]
            if isinstance(temp_field, int):  # necessary for checking @iot.id
                temp_val = int(temp_val)
            tokens.pop(0)
            return temp_val != temp_field
        elif tokens[0] == "<" or tokens[0] == ">" or tokens[0] == "<=" or tokens[0] == ">=":
            comparator = tokens[0]
            tokens.pop(0)
            temp_val = tokens[0]
            temp_val = int(temp_val)
            temp_field = int(temp_field)
            tokens.pop(0)
            if comparator == "<":
                return  temp_field < temp_val
            if comparator == "<=":
                return temp_field <= temp_val
            if comparator == ">":
                return temp_field > temp_val
            if comparator == ">=":
                return temp_field >= temp_val
        else:
            return parse_error()
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
