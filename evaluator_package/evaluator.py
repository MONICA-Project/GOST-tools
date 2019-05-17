from evaluator_package.default_functions import *
from evaluator_package.test_functions import *
from parser_definitions import init_default_parser, init_test_parser
from evaluator_package.environments import default_env, test_env

# all the evaluation methods which are always used and are checked before all other methods
always_active = [get_info]

# standard mode evaluations list
first_initialization = [user_defined_address, saved_address, ping, read_file]
default_initialization = [user_defined_address, ping, read_file]

getting_items = [get_with_check_of_command_line, select_items]
create = [create_records]
mod_items = [delete, patch, post]
show = [select_result_fields, show_results]
failure_handling = [show_failures]

first_time_ending = [clear_environment, execute_and_exit]
default_ending = [clear_environment, exit_function]


first_time_steps = [always_active, first_initialization, create, getting_items, mod_items, show,
                    failure_handling, first_time_ending]

default_steps = [always_active, default_initialization, create, getting_items, mod_items, show,
                 failure_handling, default_ending]

# test mode evaluations list
test_initialization = [started_session, create_test_records]
test_actions = [post]
test_ending = [clear_test_environment, exit_function]

test_steps = [always_active, test_initialization, test_actions, test_ending]


class EvaluatorClass:
    """reads a list of arguments and evaluates them"""

    def __init__(self, args, reading_file=False):
        self.reading_file = reading_file
        self.parser = init_default_parser()
        self.args = self.parser.parse_args(args)
        self.environment = default_env()
        self.evaluation_steps = []
        self.first_time = args  # stores the first argument given AND indicate that it is the first execution

    def evaluate(self, args=False):
        """evaluate stored args using previously
        defined lists of functions"""
        if args:
            self.init(args)
        elif self.first_time:
            self.init(self.first_time)
        else:
            print("Insert a command")
            exit(0)
        #self.args = expand_intervals(args)
        for step in self.evaluation_steps:
            for function in step:
                function(self)

    def init(self, args):
        self.args = self.parser.parse_args(args)
        if self.args.mode:
            self.select_mode(args)
        elif self.first_time:
            self.set_evaluation_steps(first_time_steps)
            self.first_time = False
        elif not self.args.mode and self.environment["mode"] == "default":  # necessary for the second execution of
            self.set_evaluation_steps(default_steps)                        # evaluation, if mode is not provided

    def select_mode(self, args):
        changed_mode = False
        if not (self.environment["mode"] == self.args.mode):
            print("exited " + self.environment["mode"] + " mode")
            changed_mode = True
        self.environment["mode"] = self.args.mode

        if self.args.mode == "test" and changed_mode:
            print("entered test mode")
            self.set_evaluation_steps(test_steps)
            self.environment = test_env()
            self.parser = init_test_parser()

        elif self.args.mode == "default":
            if self.first_time:
                self.set_evaluation_steps(first_time_steps)
            elif changed_mode:
                print("entered default mode")
                self.environment = default_env()
                self.set_evaluation_steps(default_steps)
            elif self.evaluation_steps == first_time_steps:  # necessary to change evaluation steps if
                                                             # default mode is selected before other modes
                self.environment = default_env()
                self.set_evaluation_steps(default_steps)
            self.parser = init_default_parser()

        if changed_mode:
            if args:
                self.args = self.parser.parse_args(args)  # re-parse the args with the new parser
                                                          # double parsing needed to get "--mode" value
        return changed_mode

    def set_evaluation_steps(self, steps_list):
        self.evaluation_steps = steps_list
