def needed_fields(fields, critical_failures_resistant=False):
    def decorator(function):
        def wrapper(arg):
            if bool(arg.environment["critical_failures"]) and not critical_failures_resistant:
                return False
            for i in fields:
                for j in arg.args.__dict__:
                    if bool(arg.args.__dict__[j]) and (i == j):
                        return function(arg)
            return False
        return wrapper
    return decorator

