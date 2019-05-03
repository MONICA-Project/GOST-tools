from evaluator_utilities import *
from parser_def import init_default_parser, init_test_parser

always_active = [get_info]
########################################################################################################################
first_initialization = [user_defined_address, saved_address, missing_ogc_type, ping]
default_initialization = [user_defined_address, missing_ogc_type, ping]

getting_items = [get, select_items, select_fields]
mod_items = [delete, patch, post]
show = [show_results]
failure_handling = [show_failures]

first_time_ending = [clear_environment, execute_and_exit]
default_ending = [clear_environment, exit_function]


first_time_steps = [always_active, first_initialization, getting_items, mod_items, show,
                    failure_handling, first_time_ending]

default_steps = [always_active, default_initialization, getting_items, mod_items, show,
                 failure_handling, default_ending]

#######################################################################################################################
test_initialization = [create_records, user_defined_address, ping]
test_ending = [clear_test_environment, exit_function]

test_steps = [always_active, test_initialization, test_ending]


class EvaluatorClass:

    def __init__(self, args):
        self.parser = init_default_parser()
        self.args = self.parser.parse_args(args)
        self.environment = {"selected_items": [], "critical_failures": [],
                            "non_critical_failures": [], "mode": "default", "GOST_address": None}
        self.evaluation_steps = []

    def evaluate(self, args=False):
        if args:
            self.args = self.parser.parse_args(args)
            if self.args.mode:
                self.select_mode()
                self.args = self.parser.parse_args(args) # re-parse the args with the new parser

        for step in self.evaluation_steps:
            for function in step:
                self.environment = function(self.args, self.environment)

    def init(self, first_time=False):
        if first_time and not self.args.mode:
            self.evaluation_steps = first_time_steps
        elif not self.args.mode and self.environment["mode"] == "default":
            self.set_evaluation_steps(default_steps)

    def select_mode(self):
        if self.args.mode:
            if not (self.environment["mode"] == self.args.mode):
                print("exited " + self.environment["mode"] + " mode")
            self.environment["mode"] = self.args.mode

            if self.args.mode == "test":
                print("entered test mode")
                self.set_evaluation_steps(test_steps)
                self.parser = init_test_parser()
            elif self.args.mode == "default":
                print("entered default mode")
                self.set_evaluation_steps(default_steps)
                self.parser = init_default_parser()

    def set_evaluation_steps(self, steps_list):
        self.evaluation_steps = steps_list
