from evaluator_package.evaluator import *
from evaluator_package.sql_parser import *
import shlex


def evaluate(file_path):
    if "--exit" in file_path:
        exit(0)
    file = open(file_path)
    args = file.read().replace('\n', ' ')
    args = shlex.split(args)

    from evaluator_package.evaluator import EvaluatorClass
    parsed_values = parse_args(args)

    left_result = None
    right_result = None
    try:
        left_side = parsed_values["left_side"]
        left_side += ["--silent"]
        evaluator = EvaluatorClass(left_side)
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
        right_side = parsed_values["right_side"]
        right_side += ["--silent"]
        right_result = evaluator.evaluate(parsed_values["right_side"])["results"]

    except SystemExit as e:
        if e.code == 0:
            pass
        else:
            exit(e.code)
    except BaseException as e:
        print('Raised exception : ' + str(e))
        exit(1)

    left = append_name_to_key(left_result, parsed_values['left_name'])

    right = append_name_to_key(right_result, parsed_values['right_name'])

    result = join(left, right, parsed_values["join_conditions"])

    show_result = show_filter(result, parsed_values['show'])

    for i in show_result:
        print(i)
