import copy
from evaluator_package.Parsing_tools import is_field, tokenize_parentheses

"""Implemented Grammar:
S    -> (S) S_1 | a_1 S_1 | not (S) S_1 
S_1  -> bool S S_1 | epsilon
a_1  -> a | not a
a    -> record_field comp value | value in record_field | value not in field

bool -> and | or
comp -> == | != | > | < | >= | <= | <> | gt | lt | gteq |  lteq | diff
"""

"""Methods S, S_1, a_1, a, are used to evaluates the espression"""


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

        if isinstance(result, dict):  # parsing errors
            print(result)
            return False
        elif bool(local_tokens_copy):  # error if there are non checked tokens
            return False
        return True

    except:
        return False


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
        return not a(tokens)
    else:
        return a(tokens)


def a(tokens):
    if is_value(tokens[0]):
        tokens.pop(0)
        if tokens[0] == "not":
            tokens.pop(0)
            if tokens[0] == "in":
                tokens.pop(0)
                tokens.pop(0)
                return True
            else:
                return parse_error(tokens[0])
        elif tokens[0] == "in":
            tokens.pop(0)
            tokens.pop(0)
            return True

    elif is_field(tokens[0]):
        tokens.pop(0)
        if tokens[0] == "==":
            tokens.pop(0)
            tokens.pop(0)
            return True
        elif tokens[0] == "!=":
            tokens.pop(0)
            tokens.pop(0)
            return True
        elif tokens[0] in ["<", "lt", "<=", "lteq", ">", "gt", ">=", "gteq", "<>", "diff"]:
            tokens.pop(0)
            tokens.pop(0)
            return True
        else:
            return parse_error(tokens[0])
    else:
        return parse_error(tokens[0])


def parse_error(bad_token):
    """Returns an error message and the token causing it
    """

    return {"error": f"parsing error, invalid token [{bad_token}] found"}


def is_value(token):
    """Checks if the token is a value"""
    return not (is_field(token) or token in ["(", ")", "and", "or", "in", "not"])