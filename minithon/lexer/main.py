from enum import Enum
from typing import NamedTuple, cast
import re


class TokenType(Enum):
    COMMENT = r"#.*"

    # Control flow
    IF = r"\bif\b"
    ELSE = r"\belse\b"
    ELIF = r"\belif\b"

    # Loops
    WHILE = r"\bwhile\b"
    BREAK = r"\bbreak\b"
    CONTINUE = r"\bcontinue\b"

    # Operators
    PLUS = r"\+"
    MINUS = r"-"
    MULTIPLY = r"\*"
    DIVIDE = r"/"
    MODULUS = r"%"
    EQUAL = r"=="
    NOT_EQUAL = r"!="
    GREATER_THAN = r">"
    LESS_THAN = r"<"
    ASSIGN = r"="
    AND = r"\band\b"
    OR = r"\bor\b"
    NOT = r"\bnot\b"

    # Datatypes
    BOOL_TRUE = r"\bTrue\b"
    BOOL_FALSE = r"\bFalse\b"
    INTEGER = r"\d+"
    FLOAT = r"\d+\.\d+"
    STRING = r"\".*?\"|\'.*?\'"

    # Punctuation
    COLON = r":"
    NEWLINE = r"\n"
    WHITESPACE = r"\s+"

    # Misc
    PASS = r"\bpass\b"
    IDENTIFIER = r"[a-zA-Z_]\w*"


class Token(NamedTuple):
    lexeme: str
    type: TokenType


class UnexpectedToken(Exception):
    def __init__(self, code: str, pos: int) -> None:
        line_start_pos = code.rfind("\n", 0, pos) + 1 if pos != 0 else 0
        line_end_pos = code.find("\n", pos)
        line = code[line_start_pos:line_end_pos]
        token_line_pos = pos - line_start_pos
        token = line[token_line_pos:].split(" ", 1)[0]
        highlighter = (" " * token_line_pos) + ("^" * len(token))
        err = f"{line}\n{highlighter}"
        line_number = code[:pos].count("\n") + 1
        super().__init__(f'\033[31mUnexpected token "{token}" at line {line_number}:\n{err}\033[0m')


def tokenize(code: str) -> list[Token]:
    tokens_specification = [(t.name, t.value) for t in TokenType]
    all_tokens_regex = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in tokens_specification
    )
    tokens: list[Token] = []
    pos = 0
    for match_object in re.finditer(all_tokens_regex, code):
        if match_object.start() != pos:
            raise UnexpectedToken(
                code,
                pos,
            )
        kind = cast(str, match_object.lastgroup)
        value = match_object.group()
        token = Token(value, TokenType[kind])
        tokens.append(token)
        pos = match_object.end()
    if pos != len(code):
        raise UnexpectedToken(
            code,
            pos,
        )
    return tokens
