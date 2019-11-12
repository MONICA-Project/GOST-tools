import copy
from evaluator_package.Parsing_tools import tokenize_parentheses, is_field
from evaluator_package.selection_expression_validator import is_value, S

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
                return  S_1(tokens, temp_result, record)
            else:
                return parse_error(tokens[0])

    elif is_field(tokens[0]) or is_value(tokens[0]) or tokens[0] == "not":
        temp_result = a_1(tokens, record)
        return S_1(tokens, temp_result, record)

    else:
        return parse_error(tokens[0])


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


def a_1(tokens, record=None):
    if tokens[0] == "not":
        tokens.pop(0)
        return not a(tokens, record)
    else:
        return a(tokens, record)


def a(tokens, record):
    x = tokens[0].startswith("'")
    y = tokens[0].startswith('"')
    if is_value(tokens[0]) or x or y:
        if x:
            tokens[0] = tokens[0].lstrip('\'')
            i = 0
            while i < len(tokens):
                if tokens[i].endswith("'"):
                    tokens[i] = tokens[i].rstrip('\'')
                i += 1
        elif y:
            tokens[0] = tokens[0].lstrip("\"")
            i = 0
            while i < len(tokens):
                if tokens[i].endswith('"', 1):
                    tokens[i] = tokens[i].rstrip("\"")
                i += 1
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




