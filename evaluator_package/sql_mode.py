from evaluator_package.evaluator import *


def evaluate(args):
    from evaluator_package.evaluator import EvaluatorClass
    parsed_values = parse(args)
    left_result = None
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
        right_result = evaluator.evaluate(parsed_values["right_side"])

    except SystemExit as e:
        if e.code == 0:
            pass
        else:
            exit(e.code)
    except BaseException as e:
        print('Raised exception : ' + str(e))
        exit(1)

    pass


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

# --get -t Sensors --select @iot.id < 842 as name_1 join -g -t Sensors  --select @iot.id > 842 as name_2 on name_1 name in name_2 description show name_1 name name_2 id

