from . import evaluator_utilities

def needed_fields(no_fields=None,at_least_one_field=None,
                  all_mandatory_fields=None, critical_failures_resistant=False,
                  needed_ogc = False):
    """decorator with arguments: if at least one of the field in at_least_one
    and  all the fields in all_fields are in args the decorated function is executed,
    otherwise not"""
    def decorator(function):
        def wrapper(evaluator):
            if bool(evaluator.environment["critical_failures"]) and not critical_failures_resistant:
                return False

            if no_fields:  # checking all field that will block the execution
                for i in all_mandatory_fields:
                    if bool(evaluator.args.__dict__[i]):
                        return False
            if needed_ogc:
                if not evaluator_utilities.check_and_fix_ogc(evaluator):
                    evaluator.environment["critical_failures"].append([{"error": "ogc type not defined"}])
                    return False


            required_at_least = bool(at_least_one_field)
            required_all = bool(all_mandatory_fields)
            required_at_least_confirmed = not required_at_least
            required_all_confirmed = not required_all

            if (not required_all) and (not required_at_least):
                return function(evaluator)

            if required_all:  # checking all mandatory fields
                for i in all_mandatory_fields:
                    if bool(evaluator.args.__dict__[i]):
                        required_all_confirmed = True
                    else:
                        return False

            if required_at_least and bool(evaluator.args.__dict__):  # checking at least one fields
                for i in at_least_one_field:
                    for j in evaluator.args.__dict__:
                        if bool(evaluator.args.__dict__[j]) and (i == j):
                            required_at_least_confirmed = True
                            break

            if required_at_least_confirmed and required_all_confirmed:
                return function(evaluator)
            else:
                return False

        return wrapper
    return decorator
