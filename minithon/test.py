from minithon.lexer import Token, tokenize
from pprint import pprint
from pathlib import Path
import time

CURR_ROOT_DIR = Path(__file__).parent


def test_lexer() -> list[Token]:
    with open(CURR_ROOT_DIR / "test.mipy") as f:
        contents = f.read()
        start_time = time.time()
        stop_on_error = False
        tokens, exceptions = tokenize(contents, stop_on_error)
        runtime = time.time() - start_time
        pprint(tokens)
        if not stop_on_error:
            for e in exceptions:
                print(e)
        print(f"Runtime: {runtime:.4f} seconds")
        return tokens


def test_parser(tokens: list[Token]): ...


if __name__ == "__main__":
    tokens = test_lexer()
    test_parser(tokens)
