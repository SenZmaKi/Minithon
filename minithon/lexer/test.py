from .main import tokenize
from pprint import pprint
from pathlib import Path
import time

CURR_ROOT_DIR = Path(__file__).parent


def main() -> None:
    with open(CURR_ROOT_DIR / "test.mipy") as f:
        contents = f.read()
        start_time = time.time()
        stop_on_error = True
        tokens, exceptions = tokenize(contents, stop_on_error)
        runtime = time.time() - start_time
        pprint(tokens)
        if not stop_on_error:
            [print(e) for e in exceptions]
        print(f"Runtime: {runtime:.4f} seconds")


if __name__ == "__main__":
    main()
