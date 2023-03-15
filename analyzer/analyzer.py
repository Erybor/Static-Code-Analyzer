import ast
import itertools
from regex_matcher import RegexMatcher
from ast import FunctionDef, Assign


class Analyzer(ast.NodeVisitor):
    def __init__(self, file_path, logger):
        self.file_path = file_path
        self.logger = logger

    def visit_FunctionDef(self, node: FunctionDef) -> None:
        names = [i.arg for i in node.args.args]
        for name in names:
            if not RegexMatcher.is_snake_case(name):
                self.logger.log_error(self.file_path, node.lineno - 1, 'S010', name)

        for default in itertools.chain(node.args.defaults, node.args.kw_defaults):
            if isinstance(default, (ast.Dict, ast.Set, ast.List)):
                self.logger.log_error(self.file_path, node.lineno - 1, 'S012')
        self.generic_visit(node)

    # TODO There's a problem with this approach, it checks every variable (including constants).
    def visit_Assign(self, node: Assign) -> None:
        for name in node.targets:
            if isinstance(name, ast.Name):
                if not RegexMatcher.is_snake_case(name.id):
                    self.logger.log_error(self.file_path, node.lineno - 1, 'S011', name.id)
        self.generic_visit(node)
