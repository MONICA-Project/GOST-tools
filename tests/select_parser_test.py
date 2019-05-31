from evaluator_package import selection_parser


"""
A test file for the parser of select expressions
"""

items = [{"name": "timer", "description": "default description", "metadata": "meta 1", "@iot.id": "1"},
         {"name": "thermometer", "description": "default description", "metadata": "meta 2", "@iot.id": "2"},
         {"name": "photometer", "description": "default description", "metadata": "meta 3", "@iot.id": "3"}]

tokens_1 = {"name": "1",
            "tokens": ["name", "==", "timer", "and", "description", "==", "default"],
            "expected_result": False}
tokens_2 = {"name": "2",
            "tokens": ["(", "description", "==", "default", ")"],
            "expected_result": False}
tokens_3 = {"name": "3",
            "tokens": ["name", "==", "timer", "and", "(", "description", "==", "default", ")"],
            "expected_result": False}
tokens_4 = {"name": "4",
            "tokens": ["name", "!=", "mario", "or", "(", "description", "!=", "default", ")"],
            "expected_result": True}
tokens_5 = {"name": "5",
            "tokens": ["name", "==", "timer", "and", "(", "description", "!=", "default", ")"],
            "expected_result": True}
tokens_6 = {"name": "6",
            "tokens": ["name", "==", "timer", "and", "(", "description", "==", "default description", ")"],
            "expected_result": True}
tokens_7 = {"name": "7",
            "tokens": ["name", "==", "timer", "and", "(", "1", "in", "metadata", ")"],
            "expected_result": True}
tokens_8 = {"name": "8",
            "tokens": ["name", "==", "timer","or", "name", "==", "photometer",
                       "and", "(", "1", "in", "metadata", "and", "2", "not", "in", "description", ")"],
            "expected_result": True}
tokens_9 = {"name": "9",
            "tokens": ["name", "!=", "timer", "or", "photometer", "not", "in", "name",
                       "and", "(", "1", "in", "metadata", "and", "2", "not", "in", "description", ")"],
            "expected_result": True}

t_10 = tokens_9["tokens"] + ["and"] + tokens_2["tokens"]

tokens_10 = {"name": "10",
            "tokens": t_10,
            "expected_result": False}
tokens_11 = {"name": "11",
             "tokens": ["name", "==", "timer", "or", "@iot.id", "==", "1"],
             "expected_result": True}

tokens_11_1 = {"name": "11_1",
             "tokens": ["name", "==", "timer", "or", "@iot.id", "==", "1", "random_value_1", "random_value_2"],
             "expected_result": "error"}

tokens_11_2 = {"name": "11_2",
             "tokens": ["not", "(", "name", "==", "timer", ")"],
             "expected_result": False}

tokens_11_3 = {"name": "11_3",
             "tokens": ["(", "name", "==", "timer", ")"],
             "expected_result": True}

single_record_test_list = []

single_record_test_list.append(tokens_1)
single_record_test_list.append(tokens_2)
single_record_test_list.append(tokens_3)
single_record_test_list.append(tokens_4)
single_record_test_list.append(tokens_5)
single_record_test_list.append(tokens_6)
single_record_test_list.append(tokens_7)
single_record_test_list.append(tokens_8)
single_record_test_list.append(tokens_9)
single_record_test_list.append(tokens_10)
single_record_test_list.append(tokens_11)
single_record_test_list.append(tokens_11_1)
single_record_test_list.append(tokens_11_2)
single_record_test_list.append(tokens_11_3)


tokens_12 = {"name": "12",
             "tokens": ["name", "==", "timer", "or", "@iot.id", "==", "1", "or", "(", "name", "==", "photometer",
                        "and", "metadata", "==", "meta 3", ")"],
             "expected_results": 2}
tokens_13 = {"name": "13",
             "tokens": ["@iot.id", ">", "1", "and", "@iot.id", "<=", "3"],
             "expected_results": 2}

multi_record_test_list = []
multi_record_test_list.append(tokens_12)
multi_record_test_list.append(tokens_13)


def test_single_record():
    print("Testing single record")
    for i in single_record_test_list:
        result = selection_parser.select_parser(i["tokens"], items[0])
        if isinstance(result, dict):
            if "error" in result:
                if i["expected_result"] == "error":
                    print(f"test {i['name']} passed")
                else:
                    print(f"test {i['name']} not passed, {result}")

        elif (result and i["expected_result"]) or ((not result) and (not i["expected_result"])):
            print(f"test {i['name']} passed")
        else:
            print(f"test {i['name']} not passed")


def test_multi_record():
    print("Testing multi record")
    for i in multi_record_test_list:
        counter = 0
        for j in items:
            result = selection_parser.select_parser(i["tokens"], j)
            if result:
                counter += 1
        if i["expected_results"] == counter:
            print(f"test {i['name']} passed")
        else:
            print(f"test {i['name']} not passed")


test_single_record()
test_multi_record()