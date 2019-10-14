import copy

""" Implemented Grammar:
S    -> (S) S_1 | a_1 S_1 | not (S) S_1
S_1  -> bool S S_1 | epsilon
a_1  -> a | not a
a    -> record_field comp value | value in record_field | value not in field

bool -> and | or
comp -> == | != | > | < | >= | <= | <> | gt | lt | gteq |  lteq | diff
"""

"""Methods S, S_1, a_1, a, are used to evaluates the espression"""


def select_parser(tokens, record=None):
    """Evaluates if record is true or false according to the expression in tokens. The expression must follow
    the grammar at the beginning of this document

    :param tokens: the expression, already tokenized
    :param record: the record to check
    :return: true if the record satisfy the expression, otherwise false
    """
    if not(bool(tokens)):
        return False
    tokenize_parentheses(tokens)
    local_tokens_copy = copy.deepcopy(tokens)  # necessary because the parser removes all the elements from
                                               # tokens list during evaluation
    result = S(local_tokens_copy, record)
    if isinstance(result, dict):  # bad parsing error checking
        return result
    elif bool(local_tokens_copy):  # error if there are non checked tokens or error messages
        return {"error": "bad expression, unused tokens found"}
    else:
        return result


def S(tokens, record=None):
    if tokens[0] == "(":
        tokens.pop(0)
        temp_result = S(tokens, record)
        if tokens[0] == ")":
            tokens.pop(0)
            return S_1(tokens, temp_result, record)
        else:
            return parse_error(tokens[0])
    elif tokens[0] == "not":
        tokens.pop(0)
        if tokens[0] == "(":
            tokens.pop(0)
            temp_result = not S(tokens, record)
            if tokens[0] == ")":
                tokens.pop(0)
                return S_1(tokens, temp_result, record)
            else:
                return parse_error(tokens[0])

    elif is_field(tokens[0]) or is_value(tokens[0]) or tokens[0] == "not":
        temp_result = a_1(tokens, record)
        return S_1(tokens, temp_result, record)

    else:
        return parse_error(tokens[0])


def S_1(tokens, previous_result, record=None):
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


def a_1(tokens, record=None):
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
                return parse_error(tokens[0])
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
        elif tokens[0] == "<" or tokens[0] == ">" or tokens[0] == "<=" or tokens[0] == ">=" or tokens[0] == "<>"\
                or tokens[0] == "gt" or tokens[0] == "lt" or tokens[0] == "gteq" \
                or tokens[0] == "lteq" or tokens[0] == "diff":
            comparator = tokens[0]
            tokens.pop(0)
            temp_val = tokens[0]
            temp_val = int(temp_val)
            temp_field = int(temp_field)
            tokens.pop(0)
            if comparator == "<" or comparator == "lt":
                return temp_field < temp_val
            if comparator == "<=" or comparator == "lteq":
                return temp_field <= temp_val
            if comparator == ">" or comparator == "gt":
                return temp_field > temp_val
            if comparator == ">=" or comparator == "gteq":
                return temp_field >= temp_val
            if comparator == "<>" or comparator == "diff":
                return not temp_field == temp_val
        else:
            return parse_error(tokens[0])
    else:
        return parse_error(tokens[0])


def parse_error(bad_token):
    """Returns an error message and the token causing it
    """

    return {"error": f"parsing error, invalid token [{bad_token}] found"}


def is_field(token):
    """Checks if the token is a valid ogc type field
    """

    return token in ["name", "description", "encodingType", "location", "properties", "metadata",
                     "definition", "phenomenonTime", "resultTime", "observedArea", "result", "@iot.id",
                     "resultQuality","validTime", "time", "parameters", "feature"]


def is_value(token):
    """Check if the token is a value"""
    return not (is_field(token) or token in ["(", ")", "and", "or", "in", "not"])


def tokenize_parentheses(tokens):
    """ Finds non parsed brackets in tokens (ex.: ['x(y']['z)'] -> ['x']['(']['y']['z'][')']

    :param tokens: a list of tokens
    :return: the list with unchecked brackets tokenized
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



