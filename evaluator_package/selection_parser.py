def parser(tokens, result = None):
    if not bool(tokens):
        return S(result)


def S(tokens):
    if tokens[0] == "(":
        pop[0]
        temp_result = S(tokens)
        if tokens[0] == ")":
            pop[0]
            return S_1(tokens, temp_result)
        else:
            error()

    elif is_field(tokens[0]) or is_value(tokens[0]) or tokens[0] == "not":
        temp_result = a_1(tokens)
        return S_1(tokens, temp_result)


def S_1(tokens, previous_result):
    if not(bool(tokens[0])):
        return previous_result
    if tokens[0] == "and" or "or":
        temp_bool = tokens[0]
        pop[0]
        if temp_bool == "and":
            temp_result = previous_result and S(tokens)
        elif temp_bool == "or":
            temp_result = previous_result or S(tokens)
        return S_1(tokens, temp_result)

def a_1(tokens)
    if tokens[0] == "not":
        pop[0]
        return not a(tokens)
    else:
        return a(tokens)

def a(tokens):
    if is_value(tokens[0]):
        temp_val = tokens[0]
        pop[0]
        if tokens[0] == "not":
            pop[0]
            temp_field = tokens[0]
            pop[0]
            return not temp_val in temp_field
        elif is_field(tokens[0]):
            temp_field = tokens[0]
            pop[0]
            return temp_val in temp_field
        else:
            error()
    elif is_field(tokens[0]):
        temp_field = tokens[0]
        pop[0]
        if tokens[0] == "==":
            pop[0]
            temp_val = tokens[0]
            pop[0]
            return temp_val == temp_field
        elif tokens[0] == "!=":
            pop[0]
            temp_val = tokens[0]
            pop[0]
            return temp_val != temp_field
        else:
            error()
    else:
        error()




