import copy

"""Implemented Grammar:
S    -> (S) S_1 | a_1 S_1 | not (S) S_1
S_1  -> bool S S_1 | epsilon
a_1  -> a | not a
a    -> record_field comp value | value in record_field | value not in field

bool -> and | or
comp -> == | != | > | < | >= | <= | <> | gt | lt | gteq |  lteq | diff
"""


def select_parser_validator(tokens):
    """Evaluates if the tokens follow the grammar at the beginning of this file

    :param tokens: the expression, already tokenized
    :return: true if the record satisfy the grammar, otherwise false
    """
    if not(bool(tokens)):
        return False
    tokenize_parentheses(tokens)
    local_tokens_copy = copy.deepcopy(tokens)  # necessary because the parser removes all the elements from
                                               # tokens list during evaluation
    try:
        result = S(local_tokens_copy)
        return result

    except:
        return False


def S(tokens, record=None):
    if tokens[0] == "(":
        tokens.pop(0)
        temp_result = S(tokens)
        if tokens[0] == ")":
            tokens.pop(0)
            return S_1(tokens, temp_result)
        else:
            return False
    elif tokens[0] == "not":
        tokens.pop(0)
        if tokens[0] == "(":
            tokens.pop(0)
            temp_result = S(tokens)
            if tokens[0] == ")":
                tokens.pop(0)
                return not (S_1(tokens, temp_result))
            else:
                return False

    elif is_field(tokens[0]) or is_value(tokens[0]) or tokens[0] == "not":
        temp_result = a_1(tokens)
        return S_1(tokens, temp_result)

    else:
        return False


def S_1(tokens, previous_result):
    if not(bool(tokens)):
        return previous_result

    elif tokens[0] == "and" or tokens[0] == "or":
        temp_bool = tokens[0]
        tokens.pop(0)
        temp_result = S(tokens)
        if temp_bool == "and" or temp_bool == "or":
            temp_result = previous_result and temp_result
        return S_1(tokens, temp_result)
    else:
        return previous_result


def a_1(tokens):
    if tokens[0] == "not":
        tokens.pop(0)
        return a(tokens)
    else:
        return a(tokens)


def a(tokens):
    if is_value(tokens[0]):
        temp_val = tokens[0]
        tokens.pop(0)
        if tokens[0] == "not":
            tokens.pop(0)
            if tokens[0] == "in":
                tokens.pop(0)
                tokens.pop(0)
                return True
            else:
                return False
        elif tokens[0] == "in":
            tokens.pop(0)
            tokens.pop(0)
            return True

    elif is_field(tokens[0]):
        tokens.pop(0)
        if tokens[0] == "==":
            tokens.pop(0)
            temp_val = tokens[0]
            tokens.pop(0)
            return True
        elif tokens[0] == "!=":
            tokens.pop(0)
            tokens.pop(0)
            return True
        elif tokens[0] == "<" or tokens[0] == ">" or tokens[0] == "<=" or tokens[0] == ">=" or tokens[0] == "<>"\
                or tokens[0] == "gt" or tokens[0] == "lt" or tokens[0] == "gteq" \
                or tokens[0] == "lteq" or tokens[0] == "diff":
            tokens.pop(0)

            tokens.pop(0)
            return True
        else:
            return False
    else:
        return False


def is_field(token):
    """Checks if the token is a valid ogc type field
    """

    return token in ["name", "description", "encodingType", "location", "properties", "metadata",
                     "definition", "phenomenonTime", "resultTime", "observedArea", "result", "@iot.id",
                     "resultQuality","validTime", "time", "parameters", "feature"]


def is_value(token):
    return not (is_field(token) or token in ["(", ")", "and", "or", "in", "not"])


def tokenize_parentheses(tokens):
    """Finds non parsed parentheses in tokens (ex.: ['x(y']['z)'] -> ['x']['(']['y']['z'][')']

    :param tokens: a list of tokens
    :return: the list with unchecked parenteses tokenized
    """
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