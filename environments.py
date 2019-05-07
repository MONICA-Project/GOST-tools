

def default_env(selected_items=None, results=None, critical_failures=None,
                non_critical_failures=None, mode="default",
                GOST_address=None):
    if selected_items is None:
        selected_items = []
    if results is None:
        results = []
    if critical_failures is None:
        critical_failures = []
    if non_critical_failures is None:
        non_critical_failures = []

    return {"selected_items": selected_items,
            "results": results,
            "critical_failures": critical_failures,
            "non_critical_failures": non_critical_failures,
            "mode": mode,
            "GOST_address": GOST_address
            }


def test_env(selected_items=None, results=None, critical_failures=None,
             non_critical_failures=None, mode="test",
             GOST_address=None, testing_items=None):

    if selected_items is None:
        selected_items = []
    if results is None:
        results = []
    if critical_failures is None:
        critical_failures = []
    if non_critical_failures is None:
        non_critical_failures = []
    if testing_items is None:
        testing_items = []

    return {"selected_items": selected_items,
            "results": results,
            "critical_failures": critical_failures,
            "non_critical_failures": non_critical_failures,
            "mode": mode,
            "GOST_address": GOST_address,
            "testing_items": testing_items}
