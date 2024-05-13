class CommonException(Exception):
    def __init__(
        self, msg: str, source_code: str, position: int, print_token=True
    ) -> None:
        line_start_pos = (
            source_code.rfind("\n", 0, position) + 1 if position != 0 else 0
        )
        line_end_pos = source_code.find("\n", position)
        line = source_code[line_start_pos:line_end_pos]
        token_line_pos = position - line_start_pos
        token = line[token_line_pos:].split(" ", 1)[0]
        highlighter = (" " * token_line_pos) + ("^" * len(token))
        err = f"{line}\n\033[32m{highlighter}\033[0m"
        final_err = f":\n{err}" if token else ""
        line_number = source_code[:position].count("\n") + 1
        token_str = f'\033[32m"{token}"\033[0m ' if print_token else ""
        super().__init__(
            f"\033[31m{msg} \033[0m{token_str}\033[31mat line {line_number}\033[0m{final_err}"
        )
