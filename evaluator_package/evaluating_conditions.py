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
            required_at_least_confirmed = not required_at_least
            required_all_confirmed = not required_all

            if (not required_all) and (not required_at_least):
                return function(arg)

            if required_all:  # checking all mandatory fields
                for i in all_mandatory_fields:
                    if i not in arg.args.__dict__:
                        return False
                required_all_confirmed = True

            if required_at_least:  # checking at least one fields
                for i in at_least_one_field:
                    for j in arg.args.__dict__:
                        if bool(arg.args.__dict__[j]) and (i == j):
                            required_at_least_confirmed = True
                            break


            if required_at_least_confirmed and required_all_confirmed:
                return function(arg)
            else:
                return False

        return wrapper
    return decorator
