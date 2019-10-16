def is_field(token):
    """Checks if the token is a valid ogc type field
    """

    return token in ["name", "description", "encodingType", "location", "properties", "metadata",
                     "definition", "phenomenonTime", "resultTime", "observedArea", "result", "id", "@iot.id",
                     "resultQuality", "validTime", "time", "parameters", "feature"]


def tokenize_parentheses(tokens):
    """ Finds non parsed parentheses in tokens (ex.: ['x(y']['z)'] -> ['x']['(']['y']['z'][')']

    :param tokens: a list of tokens
    :return: the list with unchecked parenteses tokenized
    """
    for index, token in enumerate(tokens):
        if ("(" in token or ")" in token) and len(token) > 1:
            parenthesis_index = token.find("(")
            parenthesis = "("
            if parenthesis_index < 0:
                parenthesis_index = token.find(")")
                parenthesis = ")"
            left_side = token[:parenthesis_index]
            right_side = token[parenthesis_index + 1:]

            del tokens[index]
            if bool(left_side):
                tokens.insert(index, left_side)
                index += 1
            tokens.insert(index, parenthesis)
            if bool(right_side):
                index += 1
                tokens.insert(index, right_side)
