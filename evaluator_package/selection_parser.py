def bool_parser(tokens, record = None):
    if not(bool(tokens)):
        return False
    return S(tokens, record)


def S(tokens, record = None):
    if tokens[0] == "(":
        tokens.pop(0)
        temp_result = S(tokens, record)
        if tokens[0] == ")":
            tokens.pop(0)
            return S_1(tokens, temp_result, record)
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
            return temp_val == temp_field
        elif tokens[0] == "!=":
            tokens.pop(0)
            temp_val = tokens[0]
            tokens.pop(0)
            return temp_val != temp_field
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


def test(record):
    tokens_1 = {"name": "1",
                "tokens": ["name", "==", "mario", "and", "description", "==", "default"],
                "expected_result": False}
    tokens_2 = {"name": "2",
                "tokens": ["(", "description", "==", "default", ")"],
                "expected_result": False}
    tokens_3 = {"name": "3",
                "tokens": ["name", "==", "mario", "and", "(", "description", "==", "default", ")"],
                "expected_result": False}
    tokens_4 = {"name": "4",
                "tokens": ["name", "!=", "mario", "or", "(", "description", "!=", "default", ")"],
                "expected_result": True}
    tokens_5 = {"name": "5",
                "tokens": ["name", "==", "mario", "and", "(", "description", "!=", "default", ")"],
                "expected_result": True}
    tokens_6 = {"name": "6",
                "tokens": ["name", "==", "mario", "and", "(", "description", "==", "default description", ")"],
                "expected_result": True}
    tokens_7 = {"name": "7",
                "tokens": ["name", "==", "mario", "and", "(", "1", "in", "metadata", ")"],
                "expected_result": True}
    tokens_8 = {"name": "8",
                "tokens": ["name", "==", "mario","or", "name", "==", "gianni",
                           "and", "(", "1", "in", "metadata", "and", "2", "not", "in", "description", ")"],
                "expected_result": True}
    tokens_9 = {"name": "9",
                "tokens": ["name", "!=", "mario", "or", "gianni", "not", "in", "name",
                           "and", "(", "1", "in", "metadata", "and", "2", "not", "in", "description", ")"],
                "expected_result": True}

    t_10 = tokens_9["tokens"] + ["and"] + tokens_2["tokens"]

    tokens_10 = {"name": "10",
                "tokens": t_10,
                "expected_result": False}

    test_list = []

    test_list.append(tokens_1)
    test_list.append(tokens_2)
    test_list.append(tokens_3)
    test_list.append(tokens_4)
    test_list.append(tokens_5)
    test_list.append(tokens_6)
    test_list.append(tokens_7)
    test_list.append(tokens_8)
    test_list.append(tokens_9)
    test_list.append(tokens_10)

    for i in test_list:
        result = bool_parser(i["tokens"], record)
        if (result and i["expected_result"]) or ((not result) and (not i["expected_result"])):
            print(f"test {i['name']} passed")
        else:
            print(f"test {i['name']} not passed")


#args = {"name" : "mario", "description" : "default description", "metadata" : "meta 1", "@iot.id" : "1"}
#test(args)
