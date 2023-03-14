import re


class RegexMatcher:
    CAMEL_CASE_PATTERN = r'([A-Z]\w+)+'
    SNAKE_CASE_PATTERN = r'(_*[a-z]+_*)+'

    @staticmethod
    def is_snake_case(word: str) -> bool:
        return bool(re.match(RegexMatcher.SNAKE_CASE_PATTERN, word))

    @staticmethod
    def is_camel_case(word: str) -> bool:
        return bool(re.match(RegexMatcher.CAMEL_CASE_PATTERN, word))

    @staticmethod
    def match_word(line: str) -> str:
        return re.search(r'\w+', line).group(0)

    @staticmethod
    def match_todo(line) -> bool:
        return bool(re.search(pattern=r'# *TODO', string=line.upper()))
