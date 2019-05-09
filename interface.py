import shlex
import sys
from evaluator_package.evaluator import EvaluatorClass


def main():
    """Creates a command evaluator_package, reads the argv input and if
    specified with the --interactive option starts a loop of
    requests"""
    evaluator = EvaluatorClass(args=sys.argv[1:])
    evaluator.evaluate()

    while True:
        new_command = shlex.split(input("(" + evaluator.environment["mode"] + " mode) insert command : "))
        evaluator.evaluate(new_command)


if __name__ == "__main__":
    main()
