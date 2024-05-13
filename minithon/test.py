from PrettyPrint.PrintLinkedList.LinkedListPrinter import Callable
from minithon.lexer import Token, tokenize
from pprint import pprint
from pathlib import Path
import time

from minithon.parser.main import Parser
from minithon.parser.types import Program

CURR_ROOT_DIR = Path(__file__).parent


def get_source_code() -> str:
    with open(CURR_ROOT_DIR / "test_code.mipy") as f:
        contents = f.read()
        return contents


def print_runtime_later(task: str) -> Callable[[], None]:
    start_time = time.time()

    def callback():
        end_time = time.time()
        runtime = end_time - start_time
        print(f"{task} runtime: {runtime:.4f} seconds")

    return callback


def test_lexer(
    source_code: str | None, show_output=True, stop_on_error=False
) -> list[Token]:
    if source_code is None:
        source_code = get_source_code()
    prt = print_runtime_later("Lexer")
    tokens, exceptions = tokenize(source_code, stop_on_error)
    if show_output:
        prt()
        pprint(tokens)
    if not stop_on_error:
        for e in exceptions:
            if show_output:
                print(e)
    return tokens


def test_parser(source_code: str | None = None, show_output=True) -> Program:
    if source_code is None:
        source_code = get_source_code()
    tokens = test_lexer(source_code, True, True)
    parser = Parser(tokens, source_code)
    prt = print_runtime_later("Parser")
    program = parser.parse()
    if show_output:
        prt()
        program.print_parse_tree()
    return program


if __name__ == "__main__":
    test_parser()
