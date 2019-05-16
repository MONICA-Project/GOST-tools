import re

def custom_split(string, custom_splitters_list):
    """splits a string by whitespace, but ignores the whitespaces inside custom_splitters_list
    example: "custom_splitters_list(a b $c d$ e f, custom_splitters_list=['$']) -> [a][b][c d][e][f]
    If founds two numbers separated by "-", converts them in a list of intermediate number: 1-4 -> [1][2][3][4]
    """
    result = []
    splitted = string.split()
    i = 0

    while i < len(splitted):  # separating by spaces and custom splitter
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

    intervals = []
    interval_indexes = []
    for index, value in enumerate(result):  # expanding intervals
        if value == "-": #TODO checking wrong inputs
            lower_bound = result[index - 1] + 1
            upper_bound = result[index + 1] - 1
            for i in range(lower_bound, upper_bound):
                intervals.append(i)
            interval_indexes.append(index)
    for i in interval_indexes:
        result.pop(i)
    result.append(intervals)

    return result

