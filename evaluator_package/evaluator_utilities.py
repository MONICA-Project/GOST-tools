import re

def custom_split(string, custom_splitters_list):
    """splits a string by whitespace, but ignores the whitespaces inside custom_splitters_list
    example: "custom_splitters_list(a b $c d$ e f, custom_splitters_list=['$']) -> [a][b][c d][e][f]
    """
    result = []
    splitted = string.split()
    i = 0

    while i < len(splitted):
        if splitted[i] not in custom_splitters_list:
            result.append(splitted[i])
            i += 1
        elif splitted[i] in custom_splitters_list:
            temp_str = ""
            cont_reading = True
            while cont_reading:
                i += 1
                if i >= len(splitted):
                    cont_reading = False
                elif splitted[i] in custom_splitters_list:
                    cont_reading = False
                    i += 1
                else:
                    temp_str += f"{str(splitted[i])}"
                    if splitted[i + 1] not in custom_splitters_list:
                        temp_str += " "

            result.append(temp_str)
    return result


