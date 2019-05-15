import re

def custom_split(string, custom_splitter):
    """splits a string by whitespace, but ignores the whitespaces inside custom_splitter
    example: "a b 'c d' e f -> [a][b][c d][e][f]
    """
    result = []

    splitted = string.split()

    i = 0

    while i < len(splitted):
        if splitted[i] != custom_splitter:
            result.append(splitted[i])
            i += 1
        elif splitted[i] == custom_splitter:
            temp_str = ""
            cont_reading = True
            while cont_reading:
                i += 1
                if i >= len(splitted):
                    cont_reading = False
                elif splitted[i] == custom_splitter:
                    cont_reading = False
                    i += 1
                else:
                    temp_str += f"{str(splitted[i])}"
                    if splitted[i + 1] != custom_splitter:
                        temp_str += " "

            result.append(temp_str)
    return result


