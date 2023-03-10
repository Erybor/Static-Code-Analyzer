import ast
import sys
import os
import re
from analyzer import Analyzer

CAMEL_CASE_PATTERN = r'([A-Z]\w+)+'
SNAKE_CASE_PATTERN = r'(_*[a-z]+_*)+'


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


class StaticCodeAnalyzer:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.empty_line_cntr = 0
        self.tree = None

    def get_error_codes(self, line):
        errors = []

        if line.strip() == '':
            self.empty_line_cntr += 1
            return

        if len(line) >= 79:
            errors.append('S001')

        # S002 - Indentation is not a multiple of four
        non_empty_idx = line.index(next(filter(lambda x: x != ' ', line)))
        if non_empty_idx % 4 != 0:
            errors.append('S002')

        # if line has semicolon and substring is not a comment
        semicolon_idx = not_in_string(line, ';')
        if semicolon_idx is not None:
            # if semicolon is not part of a comment
            if '#' not in line[:semicolon_idx]:
                errors.append('S003')

        # check if # is not in a string, i.e. if a string contains a comment.
        idx = not_in_string(line, '#')
        if idx is not None:
            # check if inline
            if line[:idx].strip() != '':
                if line[idx - 2] != ' ':
                    errors.append('S004')

        # if line contains to_do in a comment
        if re.search(pattern=r'# *TODO', string=line.upper()):
            errors.append('S005')

        if self.empty_line_cntr > 2:
            errors.append('S006')

        if 'class' in line:
            # check if the 2nd substr after class is empty
            index = line.index('class') + len('class')
            if line[index + 1] == ' ':
                errors.append('S007')
            else:
                class_name = re.search(r'\w+', line[index:]).group(0)
                if not re.match(CAMEL_CASE_PATTERN, class_name):
                    errors.append(('S008', class_name))

        if 'def' in line:
            index = line.index('def') + len('def')
            if line[index + 1] == ' ':
                errors.append('S007')
            func_name = re.search(r'\w+', line[index:]).group(0)
            if not re.match(SNAKE_CASE_PATTERN, func_name):
                errors.append(('S009', func_name))

        self.empty_line_cntr = 0

        return errors

    def get_analyzer_errors(self, dir_path, errors):
        analyzer = Analyzer(errors, dir_path)
        analyzer.visit(self.tree)

    def get_human_message(self, code, extra):
        if code == 'S001':
            return 'Too long'
        if code == 'S002':
            return 'Indentation is not a multiple of four'
        if code == 'S003':
            return 'Unnecessary semicolon'
        if code == 'S004':
            return 'At least two spaces required before inline comments'
        if code == 'S005':
            return 'TODO found'
        if code == 'S006':
            return 'More than two blank lines used before this line'
        if code == 'S007':
            return 'Too many spaces after \'class\''
        if code == 'S008':
            return f'Class name \'{extra}\' should use CamelCase'
        if code == 'S009':
            return f'Function name \'{extra}\' should use snake_case'
        if code == 'S010':
            return f'Argument name \'{extra}\' should be snake_case'
        if code == 'S011':
            return f'Variable \'{extra}\' in function should be snake_case'
        if code == 'S012':
            return f'Default argument value is mutable'

    def get_error_message(self, file_path, idx, code, extra=None):
        return f'{file_path}: Line {idx + 1}: {code} {self.get_human_message(code, extra)}'

    def analyze(self):
        arr = []

        if os.path.isdir(self.dir_path):
            for root, dirs, files in os.walk(self.dir_path):
                for file in files:
                    if file == 'tests.py':
                        continue
                    if file.endswith('.py'):
                        self.empty_line_cntr = 0
                        file_path = os.path.join(root, file)
                        with open(file_path, "r") as source:
                            self.tree = ast.parse(source.read())
                        file = open(file_path, 'r')
                        # self.tree = ast.parse(file.read())
                        # print(self.tree)
                        for idx, line in enumerate(file):
                            if line.strip() == '':
                                pass

                            errors = self.get_error_codes(line)

                            if errors is None:
                                continue
                            for e in errors:
                                extra = None
                                if isinstance(e, tuple):
                                    e, extra = e[0], e[1]
                                arr.append(self.get_error_message(file_path, idx, e, extra))
                        self.get_analyzer_errors(file_path, arr)

                        file.close()
        elif os.path.isfile(self.dir_path):

            with open(self.dir_path, "r") as source:
                self.tree = ast.parse(source.read())
            file = open(self.dir_path, 'r')

            for idx, line in enumerate(file):
                if line.strip() == '':
                    pass
                errors = self.get_error_codes(line)

                if errors is None:
                    continue

                for e in errors:
                    extra = None
                    if isinstance(e, tuple):
                        e, extra = e[0], e[1]
                    arr.append(self.get_error_message(file.name, idx, e, extra))
            self.get_analyzer_errors(self.dir_path, arr)

        for i in arr:
            print(i)


if __name__ == '__main__':
    dir_path = sys.argv[1]

    analyzer = StaticCodeAnalyzer(dir_path)
    analyzer.analyze()
