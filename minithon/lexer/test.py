from .main import tokenize
from pprint import pprint
from pathlib import Path

CURR_ROOT_DIR = Path(__file__).parent


def main() -> None:
    with open(CURR_ROOT_DIR / "test.mipy") as f:
        contents = f.read()
        tokens = tokenize(contents)
        pprint(tokens)


if __name__ == "__main__":
    main()
