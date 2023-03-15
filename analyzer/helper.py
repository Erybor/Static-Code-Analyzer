import os


# loops through the line and finds if the given character is part of a string or not.
# Returns index or None if not found.
def not_in_string(line, char):
    in_string = False
    last_char = None
    for i in range(len(line)):
        if (line[i] == '\'' or line[i] == '\"') and line[i - 1] != '\\':
            if last_char is None:
                last_char = line[i]
                in_string = True
            elif line[i] == last_char:
                in_string = False
                last_char = None
            continue
        if line[i] == char and not in_string:
            return i

    return None


def get_file_paths(path):
    paths = []
    for (path, _, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith('.py'):
                paths.append(os.path.join('.', path, filename))
    return paths
