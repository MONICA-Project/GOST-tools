def needed_fields(at_least_one_field=None, all_mandatory_fields=None, critical_failures_resistant=False):
    """decorator with arguments: if at least one of the field in at_least_one
    and  all the fields in all_fields are in args the decorated function is executed,
    otherwise not"""
    def decorator(function):
        def wrapper(arg):
            if bool(arg.environment["critical_failures"]) and not critical_failures_resistant:
                return False
            required_at_least = bool(at_least_one_field)
            required_all = bool(all_mandatory_fields)
            function_executable = False

            if (not required_all) and (not required_at_least):
                function_executable = True

            if required_at_least:  # checking at least one fields
                for i in at_least_one_field:
                    for j in arg.args.__dict__:
                        if bool(arg.args.__dict__[j]) and (i == j):
                            function_executable = True
                            break

            if required_all:  # checking all mandatory fields
                for i in all_mandatory_fields:
                    if i not in arg.args.__dict__:
                        function_executable = False
                        break
            if function_executable:
                return function(arg)
            else:
                return False

        return wrapper
    return decorator
