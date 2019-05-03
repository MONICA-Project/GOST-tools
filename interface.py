import shlex
import sys
from evaluator import EvaluatorClass


def main():
    evaluator = EvaluatorClass(args=sys.argv[1:])
    evaluator.init(first_time=True)
    evaluator.evaluate()

    while True:
        evaluator.init()
        new_command = shlex.split(input("insert command : "))
        evaluator.evaluate(new_command)


if __name__ == "__main__":
    main()
