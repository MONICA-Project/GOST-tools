class PassEnvironmentException(Exception):
    """A custom exception which passes the current environment and the current mode"""

    def __init__(self, environment=None, exit_interactive_mode=False, exit_single_command_mode=False):
        self.passed_environment = environment
        self.exit_interactive_mode = exit_interactive_mode
        self.exit_single_command_mode = exit_single_command_mode
