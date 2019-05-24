from evaluator_package.evaluator import *
import evaluator_package.sql_parser as sql_parser



def evaluate(args):
    if "--exit" in args:
        exit(0)
    from evaluator_package.evaluator import EvaluatorClass
    parsed_values = parse(args)
    left_result = None
    right_result = None
    try:
        evaluator = EvaluatorClass(parsed_values["left_side"])
        left_result = evaluator.evaluate()["results"]

    except SystemExit as e:
        if e.code == 0:
            pass
        else:
            exit(e.code)
    except BaseException as e:
        print('Raised exception : ' + str(e))
        exit(1)
    try:
        right_result = evaluator.evaluate(parsed_values["right_side"])["results"]

    except SystemExit as e:
        if e.code == 0:
            pass
        else:
            exit(e.code)
    except BaseException as e:
        print('Raised exception : ' + str(e))
        exit(1)

    left_result = append_name_to_key(left_result, parsed_values['left_name'])

    right_result = append_name_to_key(right_result, parsed_values['right_name'])

    result = join(left_result, right_result, parsed_values["join_conditions"])

    return True


def parse(args):
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
            temp_item[f"{name}_{key}"] = item[key]
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
        result.append(single_compare(left_entity, r, conditions))
    return result

def single_compare(left, right, conditions):
    matching = sql_parser.parse(left, right, conditions)
    if matching:
        return [left, right]
    else:
        return []


# --get -t Sensors --select @iot.id < 842 as name_1 join -g -t Sensors  --select @iot.id > 842 as name_2 on name_1 name in name_2 description show name_1 name name_2 id

