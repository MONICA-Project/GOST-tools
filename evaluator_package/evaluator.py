import evaluator_package.default_functions as def_func
import parser_definitions as pars_def
import evaluator_package.environments as env
import evaluator_package.exceptions as exc
import traceback

# all the evaluation functions which are always used and are checked before all other methods
always_active = [def_func.get_info]

# all the evaluation functions which are used when the mode is set on "default"
first_initialization = [def_func.user_defined_address, def_func.saved_address, def_func.ping, def_func.exec_file]
default_initialization = [def_func.user_defined_address, def_func.ping, def_func.exec_file]

getting_items = [def_func.sql_evaluate, def_func.get_command_line, def_func.related_items]  # select_items_command, related_items]
create_functions = [def_func.template, def_func.create_records]
mod_items = [def_func.delete, def_func.patch, def_func.post]
show = [def_func.select_result_fields, def_func.show_results]
failure_handling = [def_func.show_failures]

first_time_ending = [def_func.store, def_func.clear_environment, def_func.execute_and_exit]
default_ending = [def_func.store, def_func.clear_environment, def_func.exit_function]

# the steps of evaluation
first_time_steps = [always_active, first_initialization, create_functions, getting_items, mod_items, show,
                    failure_handling, first_time_ending]  # steps for first evaluation
default_steps = [always_active, default_initialization, create_functions, getting_items, mod_items, show,
                 failure_handling, default_ending]


class EvaluatorClass:
    """reads a list of arguments and evaluates them"""

    def __init__(self, args, reading_file=False, single_command=False):
        """Method to initialize evaluator"""
        self.reading_file = reading_file
        self.parser = pars_def.init_default_parser()
        self.args = args
        self.environment = env.default_env()
        self.evaluation_steps = []
        self.first_time = args  # stores the first argument given at creation time
        # AND indicates that it is the first execution
        self.single_command = single_command

    def evaluate(self, args=False):
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
                    function(self)
                except exc.PassEnvironmentException as e:
                    if self.single_command:
                        exit(0)
                    if bool(e.passed_environment):
                        return e.passed_environment
                    if e.exit_interactive_mode:
                        exit(0)
                    else:
                        print('Raised exception: ' + str(e))  # managing unexpected exceptions
                        print(traceback.format_exc())

    def init(self, args):
        """Sets the evaluator variables before the evaluation loop

        :param args: the args provided from upper layer, if "mode" is in args, change the evaluator modality
        """

        self.args = self.parser.parse_args(args)
        if self.args.mode:
            self.select_mode(args)
        elif self.first_time:
            self.set_evaluation_steps(first_time_steps)
            self.first_time = False
        elif not self.args.mode and self.environment["mode"] == "default":  # necessary for the second execution of
            self.set_evaluation_steps(default_steps)  # evaluation, if mode is not provided

    def select_mode(self, args):
        """Selects the operation mode
        """

        changed_mode = False
        if not (self.environment["mode"] == self.args.mode):
            print("exited " + self.environment["mode"] + " mode")
            changed_mode = True
        self.environment["mode"] = self.args.mode

        if self.args.mode == "default":
            if self.first_time:
                self.set_evaluation_steps(first_time_steps)
            elif changed_mode:
                print("entered default mode")
                self.environment = env.default_env(single_command=self.single_command)
                self.set_evaluation_steps(default_steps)
            elif self.evaluation_steps == first_time_steps:  # necessary to change evaluation steps if
                # default mode is selected before other modes
                self.environment = env.default_env()
                self.set_evaluation_steps(default_steps)
            self.parser = pars_def.init_default_parser()

        if changed_mode:
            if args:
                self.args = self.parser.parse_args(args)  # re-parse the args with the new select_parser
                # double parsing needed to get "--mode" value
        return changed_mode

    def set_evaluation_steps(self, steps_list):
        """To set the evaluation steps"""
        self.evaluation_steps = steps_list
