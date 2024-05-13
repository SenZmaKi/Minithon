from typing import Any, Sequence
import colorama
from minithon.lexer import Token
from PrettyPrint import PrettyPrintTree


class Node:
    def __init__(self, value: Any, children: Sequence["NodeWrapper"] = []) -> None:
        self.value = value
        self.children = children

    # Purely for debugging purposes
    def dirty_tree_str(self) -> str:
        string = str(self.value)
        if self.children:
            space_count = len(string) // 2
            space = " " * space_count
            children_string = " | ".join(
                child.node.dirty_tree_str() for child in self.children
            )
            string += f"\n{space}|{space}\n{space}V{space}\n{children_string}"
        return string


class NodeWrapper:
    def __init__(self, children: Sequence["NodeWrapper"] = []) -> None:
        self.node = Node(self, children)


class Expression(NodeWrapper):
    def __init__(
        self,
        left_operand: "Token | Expression",
        operator: "Token | None" = None,
        right_operand: "Token | Expression | None" = None,
    ) -> None:
        self.left_operand = left_operand
        self.operator = operator
        self.right_operand = right_operand
        super().__init__()

    def __str__(self) -> str:
        left_operand = (
            self.left_operand.lexeme
            if isinstance(self.left_operand, Token)
            else str(self.left_operand)
        )
        right_operand: str | None = None
        if isinstance(self.right_operand, Token):
            right_operand = self.right_operand.lexeme
        elif isinstance(self.right_operand, Expression):
            right_operand = str(self.right_operand)
        operator = self.operator.lexeme if isinstance(self.operator, Token) else None
        string = (
            f"{left_operand} {operator} {right_operand}"
            if right_operand is not None and operator is not None
            else left_operand
        )
        return string


class ControlFlowStmtBlock(NodeWrapper):
    def __init__(
        self, statement: Token, expression: Expression | None, block: "Block"
    ) -> None:
        self.statement = statement
        self.expression = expression
        self.block = block
        super().__init__([block])

    def __str__(self) -> str:
        statement_string = (
            f"{self.statement.lexeme} {self.expression}:"
            if self.expression is not None
            else f"{self.statement.lexeme}:"
        )
        block_string = str(self.block)
        spaces_count = (len(statement_string) - len(block_string)) // 2
        string = f"{statement_string}\n{' '*spaces_count}{block_string}"
        return string


class IfStatementBlock(NodeWrapper):
    def __init__(
        self,
        if_statement: ControlFlowStmtBlock,
        elifs: list[ControlFlowStmtBlock],
        else_statement: ControlFlowStmtBlock | None,
    ) -> None:
        self.if_statement = if_statement
        self.elif_statement = elifs
        self.else_statement = else_statement
        children = [if_statement]
        children.extend(elifs)
        if else_statement is not None:
            children.append(else_statement)
        super().__init__(children)

    def __str__(self) -> str:
        return "IF_STMT_BLOCK"


class GenericStatement(NodeWrapper):
    def __init__(self, token: Token, string: str) -> None:
        self.token = token
        self.string = string
        super().__init__()

    def __str__(self) -> str:
        return self.string


class AssignmentStatement(NodeWrapper):
    def __init__(
        self,
        identifier_token: Token,
        expression: Expression,
    ) -> None:
        self.identifier = identifier_token
        identifier_expression = Expression(identifier_token)
        self.expression = expression
        super().__init__([identifier_expression, expression])

    def __str__(self) -> str:
        return "ASSIGN_STMT"


class Block(NodeWrapper):
    def __init__(
        self,
        statements: list["StatementType"],
        id_: int,
        indent: int,
    ) -> None:
        self.statements = statements
        self.id = id_
        self.indent = indent
        super().__init__(statements)

    def __str__(self) -> str:
        return f"BLOCK #{self.id}"


class Program(NodeWrapper):
    def __init__(self, block: Block | None) -> None:
        self.block = block
        super().__init__([block] if block is not None else [])

    def __str__(self) -> str:
        return "PROGRAM"

    def print_parse_tree(self, pretty=True) -> None:
        if not pretty:
            print(self.node.dirty_tree_str())
            return

        def get_children(node_wrapper: NodeWrapper):
            return node_wrapper.node.children

        def get_value(node_wrapper: NodeWrapper):
            return str(node_wrapper.node.value)

        pt = PrettyPrintTree(get_children, get_value, color=colorama.Back.LIGHTCYAN_EX)  # type: ignore
        pt(self)  # type: ignore


StatementType = (
    AssignmentStatement | GenericStatement | IfStatementBlock | ControlFlowStmtBlock
)
