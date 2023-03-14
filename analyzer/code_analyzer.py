import ast
import sys
import os
# import re
from analyzer import Analyzer
from regex_matcher import RegexMatcher
from Error import Error, ErrorMessage, ErrorLogger

CAMEL_CASE_PATTERN = r'([A-Z]\w+)+'
SNAKE_CASE_PATTERN = r'(_*[a-z]+_*)+'
MAX_LINE_LENGTH = 79


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
                paths.append(os.path.join('..', path, filename))
    return paths


class StaticCodeAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.empty_line_cntr = 0
        self.tree = None
        self.logger = ErrorLogger()
        self.matcher = RegexMatcher()

    def log_error(self, code, line, name=''):
        text = ErrorMessage.get_human_message(code, name)
        # error = Error(self.file_path, line, code, text)

        self.logger.add_error(Error(self.file_path, line, code, text))

    def log_error_codes(self, line: str, line_num: int):
        if line.strip() == '':
            self.empty_line_cntr += 1
            return

        if len(line) >= MAX_LINE_LENGTH:
            self.log_error('S001', line_num)

        # S002 - Indentation is not a multiple of four
        non_empty_idx = line.index(next(filter(lambda x: x != ' ', line)))
        if non_empty_idx % 4 != 0:
            self.log_error('S002', line_num)

        # if line has semicolon and substring is not a comment
        semicolon_idx = not_in_string(line, ';')
        if semicolon_idx is not None:
            # if semicolon is not part of a comment
            if '#' not in line[:semicolon_idx]:
                self.log_error('S003', line_num)
                # errors.append('S003')

        # check if # is not in a string, i.e. if a string contains a comment.
        idx = not_in_string(line, '#')
        if idx is not None:
            # check if inline
            if line[:idx].strip() != '':
                if line[idx - 2] != ' ':
                    self.log_error('S004', line_num)
                    # errors.append('S004')

        # if line contains to_do in a comment
        if RegexMatcher.match_todo(line):
            self.log_error('S005', line_num)

        if self.empty_line_cntr > 2:
            self.log_error('S006', line_num)

        if 'class' in line:
            # check if the 2nd substr after class is empty
            index = line.index('class') + len('class')
            if line[index + 1] == ' ':
                self.log_error('S007', line_num)
            else:
                # RegexMatcher.search(pattern='\w+', word=line[index:])
                class_name = RegexMatcher.match_word(line=line[index:])
                # class_name = re.search(r'\w+', line[index:]).group(0)
                if not RegexMatcher.is_camel_case(class_name):
                    self.log_error('S008', line_num, class_name)

        if 'def' in line:
            index = line.index('def') + len('def')
            if line[index + 1] == ' ':
                self.log_error('S007', line_num)
            func_name = RegexMatcher.match_word(line=line[index:])
            if not RegexMatcher.is_snake_case(func_name):
                self.log_error('S009', line_num, func_name)

        self.empty_line_cntr = 0

        # return errors

    def get_analyzer_errors(self, dir_path, errors):
        analyzer = Analyzer(errors, dir_path)
        analyzer.visit(self.tree)

    # def get_error_message(self, file_path, idx, code, extra=None):
    #     return f'{file_path}: Line {idx + 1}: {code} {get_human_message(code, extra)}'

    def analyze_file(self, file_path) -> None:

        # with open(self.dir_path, "r") as source:
        #     self.tree = ast.parse(source.read())

        file = open(file_path, 'r')
        blank_count = 0

        for line_num, line in enumerate(file):
            self.log_error_codes(line, line_num)

        self.logger.log()

    def analyze(self):
        self.analyze_file(self.file_path)

        # if os.path.isfile(path):
        #     self.analyze_file()
        #     pass
        # else:
        #     paths = get_file_paths(path)
        #     for p in paths:
        #         self.analyze_file()


if __name__ == '__main__':
    dir_path = sys.argv[1]

    analyzer = StaticCodeAnalyzer(dir_path)
    analyzer.analyze()
