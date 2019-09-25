def checkConditions(specs, content):
    """#iterate all elements of specs (array) in content (dictionary)
    and apply the correspondent function

    """
    result = []
    for key, value in specs.items():
        controlResult = value(content.get(key))
        if controlResult:
            result.append(controlResult)
    return result
