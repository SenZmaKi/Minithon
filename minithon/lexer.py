from enum import Enum
from typing import NamedTuple, cast
import re
from functools import cache

from minithon.common import CommonException


class OperatorType(Enum):
    # Arithmetic
    ADD = r"\+"
    SUBTRACT = r"-"
    MULTIPLY = r"\*"
    DIVIDE = r"/"
    MODULUS = r"%"
    # Logical
    EQUAL = r"=="
    GREATER_THAN_OR_EQUAL = r">="
    LESS_THAN_OR_EQUAL = r"<="
    NOT_EQUAL = r"!="
    GREATER_THAN = r">"
    LESS_THAN = r"<"
    ASSIGN = r"="  # Assignment
    AND = r"\band\b"
    OR = r"\bor\b"
    NOT = r"\bnot\b"


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
    # Arithmetic
    ADD = r"\+"
    SUBTRACT = r"-"
    MULTIPLY = r"\*"
    DIVIDE = r"/"
    MODULUS = r"%"
    # Logical
    EQUAL = r"=="
    GREATER_THAN_OR_EQUAL = r">="
    LESS_THAN_OR_EQUAL = r"<="
    NOT_EQUAL = r"!="
    GREATER_THAN = r">"
    LESS_THAN = r"<"
    ASSIGN = r"="  # Assignment
    AND = r"\band\b"
    OR = r"\bor\b"
    NOT = r"\bnot\b"

    # Datatypes
    BOOL_TRUE = r"\bTrue\b"
    BOOL_FALSE = r"\bFalse\b"
    FLOAT = r"\d+\.\d+"
    INTEGER = r"\d+"
    STRING = r"\".*?\"|\'.*?\'"

    # Punctuation
    LPAREN = r"\("
    RPAREN = r"\)"
    COLON = r":"
    NEWLINE = r"\n"
    WHITESPACE = r"\s"

    # Misc
    PASS = r"\bpass\b"
    IDENTIFIER = r"[a-zA-Z_]\w*"
    EOF = r"$"


@cache
def all_tokens_regex() -> str:
    tokens_specification = [(t.name, t.value) for t in TokenType]
    combined = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in tokens_specification
    )
    return combined


class Token(NamedTuple):
    lexeme: str
    type: TokenType
    position: int


class UnrecognizedToken(CommonException):
    def __init__(self, source_code: str, position: int) -> None:
        super().__init__("Unrecognized token", source_code, position, True)


def tokenize(
    code: str, stop_on_error=False
) -> tuple[list[Token], list[UnrecognizedToken]]:
    tokens: list[Token] = []
    pos = 0
    exceptions: list[UnrecognizedToken] = []
    for match_object in re.finditer(all_tokens_regex(), code):
        if match_object.start() != pos:
            e = UnrecognizedToken(
                code,
                pos,
            )
            if stop_on_error:
                raise e
            exceptions.append(e)
        kind = cast(str, match_object.lastgroup)
        value = match_object.group()
        token = Token(value, TokenType[kind], pos)
        tokens.append(token)
        pos = match_object.end()
    if pos != len(code):
        e = UnrecognizedToken(
            code,
            pos,
        )
        if stop_on_error:
            raise e
        exceptions.append(e)
    return tokens, exceptions
