import shlex
import sys
from evaluator_package.evaluator import EvaluatorClass


def main():
    """Creates a command evaluator_package, reads the argv input and if
    specified with the --interactive option starts a loop of
    requests"""
    try:
        evaluator = EvaluatorClass(args=sys.argv[1:])
        evaluator.evaluate()
    except SystemExit as e:
        exit(e.code)
    except BaseException as e:
        print('Raised exception: ' + str(e))
        exit(1)

    while True:
        try:
            new_command = shlex.split(input("(" + evaluator.environment["mode"] + " mode) insert command : "))
            evaluator.evaluate(new_command)
        except SystemExit as e:
            if e.code == 0:
                if "--exit" in new_command:
                    exit(0)
            else:
                print('Raised SystemExit exception, -h to see commands usage')
        except BaseException as e:
            print('Raised exception: ' + str(e))


if __name__ == "__main__":
    main()
