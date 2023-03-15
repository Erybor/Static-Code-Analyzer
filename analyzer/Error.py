from dataclasses import dataclass


@dataclass
class Error:
    file_path: str
    line: int
    code: str
    text: str = ''

    def __str__(self):
        return f'{self.file_path}: Line {int(self.line) + 1}: {self.code} {self.text}'


class ErrorMessage:
    @staticmethod
    def get_human_message(code, name=''):
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
            return f'Class name \'{name}\' should use CamelCase'
        if code == 'S009':
            return f'Function name \'{name}\' should use snake_case'
        if code == 'S010':
            return f'Argument name \'{name}\' should be snake_case'
        if code == 'S011':
            return f'Variable \'{name}\' in function should be snake_case'
        if code == 'S012':
            return f'Default argument value is mutable'


class ErrorLogger:
    def __init__(self):
        self.errors = []

    def _add_error(self, error: Error) -> None:
        self.errors.append(error)

    def log_error(self, file_path, line, code, name=''):
        text = ErrorMessage.get_human_message(code, name)
        self._add_error(Error(file_path, line, code, text))

    def log(self) -> None:
        for error in sorted(self.errors, key=lambda x: (x.file_path, x.line, x.code)):
            print("ERROR:", error)

    def clear(self) -> None:
        self.errors = []
