import evaluator_package.sql_parser as sql_pars
import shlex


def evaluate(evaluator):
    """It tooks and evaluate the file provided by the user"""
    file_path = evaluator.args.sql
    if "--exit" in file_path:
        exit(0)
    file = open(file_path)
    args = file.read().replace('\n', ' ')
    args = shlex.split(args)

    from evaluator_package.evaluator import EvaluatorClass
    parsed_values = sql_pars.parse_args(args)

    left_result = None
    right_result = None
    try:
        left_side = parsed_values["left_side"]
        left_evaluator = EvaluatorClass(left_side)
        left_result = left_evaluator.evaluate()["results"]
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
        right_evaluator = EvaluatorClass(right_side)
        right_result = right_evaluator.evaluate()["results"]
    except SystemExit as e:
        if e.code == 0:
            pass
        else:
            exit(e.code)
    except BaseException as e:
        print('Raised exception : ' + str(e))
        exit(1)

    left = sql_pars.append_name_to_key(left_result, parsed_values['left_name'])
    left_name = parsed_values['left_name']
    right = sql_pars.append_name_to_key(right_result, parsed_values['right_name'])
    right_name = parsed_values['right_name']
    result = sql_pars.join(left, right, parsed_values["join_conditions"], left_name, right_name)
    show_result = sql_pars.show_filter(result, parsed_values['show'])
    return show_result
