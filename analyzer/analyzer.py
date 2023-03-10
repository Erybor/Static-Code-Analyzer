import ast
import itertools
import re
from ast import FunctionDef, Assign

CAMEL_CASE_PATTERN = r'([A-Z]\w+)+'
SNAKE_CASE_PATTERN = r'(_*[a-z]+_*)+'


class Analyzer(ast.NodeVisitor):
    def __init__(self, errors, dir_path):
        self.errors = errors
        self.dir_path = dir_path

    def visit_FunctionDef(self, node: FunctionDef) -> None:
        names = [i.arg for i in node.args.args]
        for name in names:
            if not re.match(SNAKE_CASE_PATTERN, name):
                self.errors.append(
                    f'{self.dir_path}: Line {node.lineno}: S010 Default argument name {name} should be snake_case')

        for default in itertools.chain(node.args.defaults, node.args.kw_defaults):
            if isinstance(default, (ast.Dict, ast.Set, ast.List)):
                self.errors.append(f'{self.dir_path}: Line {node.lineno}: S012 Default argument value is mutable')
        self.generic_visit(node)

    # There's a problem with this approach, it checks every variable (including constants).
    def visit_Assign(self, node: Assign) -> None:
        for name in node.targets:
            if isinstance(name, ast.Name):
                if not re.match(SNAKE_CASE_PATTERN, name.id):
                    self.errors.append(
                        f'{self.dir_path}: Line {node.lineno}: S011 Variable {name} in function should be snake_case')
        self.generic_visit(node)
