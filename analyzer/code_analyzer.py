import ast
import sys
import os
from analyzer import Analyzer
from regex_matcher import RegexMatcher
from Error import ErrorLogger

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
                paths.append(os.path.join('.', path, filename))
    return paths


class StaticCodeAnalyzer:
    def __init__(self):
        # self.file_path = file_path
        self.empty_line_cntr = 0
        self.tree = None
        self.logger = ErrorLogger()
        self.matcher = RegexMatcher()

    def log_error_codes(self, file_path, line: str, line_num: int):
        if line.strip() == '':
            self.empty_line_cntr += 1
            return

        if len(line) >= MAX_LINE_LENGTH:
            self.logger.log_error(file_path, line_num, 'S001')

        # S002 - Indentation is not a multiple of four
        non_empty_idx = line.index(next(filter(lambda x: x != ' ', line)))
        if non_empty_idx % 4 != 0:
            self.logger.log_error(file_path, line_num, 'S002')

        # if line has semicolon and substring is not a comment
        semicolon_idx = not_in_string(line, ';')
        if semicolon_idx is not None:
            # if semicolon is not part of a comment
            if '#' not in line[:semicolon_idx]:
                self.logger.log_error(file_path, line_num, 'S003')
                # errors.append('S003')

        # check if # is not in a string, i.e. if a string contains a comment.
        idx = not_in_string(line, '#')
        if idx is not None:
            # check if inline
            if line[:idx].strip() != '':
                if line[idx - 2] != ' ':
                    self.logger.log_error(file_path, line_num, 'S004')
                    # errors.append('S004')

        # if line contains to_do in a comment
        if RegexMatcher.match_todo(line):
            self.logger.log_error(file_path, line_num, 'S005')

        if self.empty_line_cntr > 2:
            self.logger.log_error(file_path, line_num, 'S006')

        if 'class' in line:
            # check if the 2nd substr after class is empty
            index = line.index('class') + len('class')
            if line[index + 1] == ' ':
                self.logger.log_error(file_path, line_num, 'S007')
            else:
                # RegexMatcher.search(pattern='\w+', word=line[index:])
                class_name = RegexMatcher.match_word(line=line[index:])
                # class_name = re.search(r'\w+', line[index:]).group(0)
                if not RegexMatcher.is_camel_case(class_name):
                    self.logger.log_error(file_path, line_num, 'S008', class_name)

        if 'def' in line:
            index = line.index('def') + len('def')
            if line[index + 1] == ' ':
                self.logger.log_error(file_path, line_num, 'S007')
            func_name = RegexMatcher.match_word(line=line[index:])
            if not RegexMatcher.is_snake_case(func_name):
                self.logger.log_error(file_path, line_num, 'S009', func_name)

        self.empty_line_cntr = 0

        # return errors

    def get_analyzer_errors(self, file_path):
        analyzer = Analyzer(file_path, self.logger)
        analyzer.visit(self.tree)

    def analyze_file(self, file_path) -> None:
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file):
                self.log_error_codes(file_path, line, line_num)

        with open(file_path, "r") as source:
            self.tree = ast.parse(source.read())
            self.get_analyzer_errors(file_path)

        self.logger.log()

    def analyze(self, path):
        if os.path.isfile(path):
            print("PATH:", path)
            self.analyze_file(path)
        else:
            paths = get_file_paths(path)
            for p in paths:
                self.analyze_file(p)
                self.logger.clear()


if __name__ == '__main__':
    dir_path = sys.argv[1]

    static_code_analyzer = StaticCodeAnalyzer()
    static_code_analyzer.analyze(dir_path)
