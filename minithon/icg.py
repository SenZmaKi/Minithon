from typing import Callable, cast
from minithon.common import CommonException
from minithon.lexer import Token, TokenType
from minithon.parser.types import (
    AssignmentStatement,
    Block,
    ControlFlowStmtBlock,
    Expression,
    GenericStatement,
    IfStatementBlock,
    Program,
)


class RuntimeError(CommonException):
    def __init__(
        self, msg: str, source_code: str, position: int, print_token=True
    ) -> None:
        super().__init__(msg, source_code, position, print_token)


class ICG:
    def __init__(self) -> None:
        self.intermediate_code = ""
        self.reg_count = 0
        self.label_count = 0
        self.identifier_to_register: dict[str, str] = {}
        self.while_label = ""
        self.while_exit_label = ""
        self.source_code: str
        self.reuse_registers: bool

    def generate(
        self, program: Program, source_code: str, reuse_registers=False
    ) -> str:
        self.source_code = source_code
        self.reuse_registers = reuse_registers
        if program.block is None:
            return self.intermediate_code
        self.block(program.block)
        return self.intermediate_code

    def block(self, block: Block) -> None:
        orig_reg_count = self.reg_count
        for stmt in block.statements:
            if isinstance(stmt, AssignmentStatement):
                self.assignment_stmt(stmt)
            elif isinstance(stmt, IfStatementBlock):
                self.if_stmt(stmt)
            elif isinstance(stmt, ControlFlowStmtBlock):
                self.while_stmt(stmt)
            else:
                self.generic_stmt(stmt)
        added_regs = [
            f"r{reg}" for reg in range(orig_reg_count + 1, self.reg_count + 1)
        ]
        items = list(self.identifier_to_register.items())
        for identifier, reg in items:
            if reg in added_regs:
                self.identifier_to_register.pop(identifier)
        if self.reuse_registers:
            self.reg_count = orig_reg_count

    def generic_stmt(
        self,
        stmt: GenericStatement,
    ) -> None:
        if not self.while_label or not self.while_exit_label:
            return
        if stmt.token.type == TokenType.CONTINUE:
            self.update_intermediate_code(f"goto {self.while_label}")
        elif stmt.token.type == TokenType.BREAK:
            self.update_intermediate_code(f"goto {self.while_exit_label}")

    def while_stmt(self, stmt: ControlFlowStmtBlock) -> None:
        self.while_label = self.get_label()
        self.update_intermediate_code(f"{self.while_label}:")
        stmt.expression = cast(Expression, stmt.expression)
        reg = self.expression_register(stmt.expression)
        self.while_exit_label = self.get_label()
        self.update_intermediate_code(f"if (!{reg}) goto {self.while_exit_label}")
        self.block(stmt.block)
        self.update_intermediate_code(f"goto {self.while_label}:")
        self.update_intermediate_code(f"{self.while_exit_label}:")

    def if_stmt(self, stmt: IfStatementBlock) -> None:
        def get_block(
            stmt: ControlFlowStmtBlock, exit_label: str
        ) -> Callable[[], None]:
            if stmt.keyword.type != TokenType.ELSE:
                stmt.expression = cast(Expression, stmt.expression)
                reg = self.expression_register(stmt.expression)
                label = self.get_label()
                self.update_intermediate_code(f"if ({reg}) goto {label}")

                def block() -> None:
                    self.update_intermediate_code(f"{label}:")
                    self.block(stmt.block)
                    self.update_intermediate_code(f"goto {exit_label}")
            else:

                def block() -> None:
                    self.block(stmt.block)

            return block

        exit_label = self.get_label()
        blocks: list[Callable[[], None]] = []
        blocks.append(get_block(stmt.if_statement, exit_label))
        for elif_ in stmt.elif_statements:
            blocks.append(get_block(elif_, exit_label))
        if stmt.else_statement is not None:
            blocks.append(get_block(stmt.else_statement, exit_label))
        for b in blocks:
            b()
        self.update_intermediate_code(f"{exit_label}:")

    def get_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def assignment_stmt(self, stmt: AssignmentStatement) -> None:
        expr_reg = self.expression_register(stmt.expression)
        if (id_reg := self.identifier_register(stmt.identifier)) is not None:
            self.update_intermediate_code(f"{id_reg} = {expr_reg}")
        self.identifier_to_register[stmt.identifier.lexeme] = expr_reg

    def identifier_register(self, token: Token) -> str | None:
        if token.type == TokenType.IDENTIFIER:
            return self.identifier_to_register.get(token.lexeme, None)

    def load_value_into_register(self, val: str) -> str:
        reg = self.get_register()
        self.update_intermediate_code(f"{reg} = {val}")
        return reg

    def expression_register(self, expr: Expression, reg: str | None = None) -> str:
        def operand_register(operand: Token | Expression) -> str:
            if isinstance(operand, Token):
                if operand.type == TokenType.IDENTIFIER:
                    if (
                        identifier_reg := self.identifier_register(operand)
                    ) is not None:
                        return self.load_value_into_register(identifier_reg)
                    raise RuntimeError(
                        "Undefined variable",
                        self.source_code,
                        operand.position,
                    )
                return self.load_value_into_register(operand.lexeme)
            return self.expression_register(operand)

        left_reg = operand_register(expr.left_operand)
        if expr.right_operand is None or expr.operator is None:
            return left_reg
        right_reg = operand_register(expr.right_operand)
        if reg is None:
            reg = self.get_register()
        operator = expr.operator.lexeme
        if expr.operator.type == TokenType.OR:
            operator = "|"
        elif expr.operator.type == TokenType.AND:
            operator = "&"
        elif expr.operator.type == TokenType.NOT:
            operator = "!"
        self.update_intermediate_code(f"{reg} = {left_reg} {operator} {right_reg}")
        return reg

    def get_register(self) -> str:
        self.reg_count += 1
        return f"r{self.reg_count}"

    def update_intermediate_code(self, val: str) -> None:
        self.intermediate_code = f"{self.intermediate_code}\n{val}"
