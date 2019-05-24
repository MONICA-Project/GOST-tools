from evaluator_package.default_functions import *
from evaluator_package.test_functions import *
from evaluator_package.sql_functions import *
from evaluator_package.evaluator_utilities import *
from parser_definitions import *
from evaluator_package.environments import *
import evaluator_package.sql_mode as sql_mode

# all the evaluation functions which are always used and are checked before all other methods
always_active = [get_info]

# all the evaluation functions which are used when the mode is set on "default"
first_initialization = [user_defined_address, saved_address, ping, exec_file]
default_initialization = [user_defined_address, ping, exec_file]

getting_items = [get_command_line, select_items_command]
create_functions = [template, create_records]
mod_items = [delete, patch, post]
show = [select_result_fields, show_results]
failure_handling = [show_failures]

first_time_ending = [store, clear_environment, execute_and_exit]
default_ending = [store, clear_environment, exit_function]

# the steps of evaluation
first_time_steps = [always_active, first_initialization, create_functions, getting_items, mod_items, show,
                    failure_handling, first_time_ending]

default_steps = [always_active, default_initialization, create_functions, getting_items, mod_items, show,
                 failure_handling, default_ending]

# all the evaluation functions which are used when the mode is set on "test"
test_initialization = [started_session, create_test_records]
test_actions = [post]
test_ending = [clear_test_environment, exit_function]

test_steps = [always_active, test_initialization, test_actions, test_ending]

# all the evaluation functions which are used when the mode is set on "sql"
sql_initialization = []
sql_actions = [sql_parsing, show_results]

sql_ending = [exit_function]

sql_steps = [always_active, sql_initialization, default_ending]


class EvaluatorClass:
    """reads a list of arguments and evaluates them"""

    def __init__(self, args, reading_file=False, silent=False):
        self.reading_file = reading_file
        self.parser = init_default_parser()
        self.args = self.parser.parse_args(args)
        self.environment = default_env()
        self.evaluation_steps = []
        self.first_time = args  # stores the first argument given at creation time
                                # AND indicates that it is the first execution
        self.silent = silent

    def evaluate(self, args=False, silent=False):
        """evaluate args using the current evaluator's evaluation steps

        :param args: the command provided from the upper layer, if defined, otherwise the one stored
                    as evaluator attribute

        :returns : returns the results of the user defined request
        """
        if args:
            self.init(args)
        elif self.first_time:
            self.init(self.first_time)
        else:
            print("Insert a valid command")
            exit(0)



        for argument in self.args.__dict__:  # adding the @ to iot.id, for shells who doesn't accept special characters
            current_argument = self.args.__dict__[argument]
            if bool(current_argument) and bool(current_argument) and isinstance(current_argument, list):
                if "iot.id" in self.args.__dict__[argument]:
                    for index, item in enumerate(current_argument):
                        if item == "iot.id":
                            current_argument[index] = "@iot.id"

        for step in self.evaluation_steps:
            for function in step:
                try:
                    if silent:
                        self.mute()
                    function(self)
                except pass_environment_Exception as e:
                    if bool(e.passed_environment):
                        return e.passed_environment
                    if e.exit_interactive_mode:
                        exit(0)
                    if e.exit_single_command_mode:
                        exit(0)
                    else:
                        print('Raised exception: ' + str(e))

    def init(self, args):
        """Sets the evaluator variables before the evaluation loop

        :param args: the args provided from upper layer, if "mode" is in args, change the evaluator modality
        """

        if self.environment["mode"] == "sql":
            sql_mode.evaluate(args[0])

        else:
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
            self.parser = init_sql_parser()

        elif self.args.mode == "sql" and changed_mode:
            print("entered sql mode")
            self.set_evaluation_steps(sql_steps)
            self.environment = sql_env()
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
                self.args = self.parser.parse_args(args)  # re-parse the args with the new select_parser
                                                          # double parsing needed to get "--mode" value
        return changed_mode

    def set_evaluation_steps(self, steps_list):
        self.evaluation_steps = steps_list

    def mute(self):
        self.silent = True
