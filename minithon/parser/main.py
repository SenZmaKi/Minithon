from typing import NoReturn
from minithon.lexer import Token, TokenType
from minithon.parser.types import (
    Node,
    Expression,
    ControlFlowStmtBlock,
    IfStatementBlock,
    GenericStatement,
    AssignmentStatement,
    StatementType,
    Block,
    Program,
)


class Parser:
    def __init__(self, tokens: list[Token], source_code: str) -> None:
        self.tokens = tokens
        self.current_token: Token
        self.token_index = -1
        self.current_node: Node
        self.source_code = source_code
        self.block_id = 0

    def raise_syntax_error(self, msg: str) -> NoReturn:
        raise SyntaxError(msg, self.source_code, self.current_token.position)

    def parse(self) -> Program:
        return self.program()

    def program(self) -> Program:
        block = self.block(-1)
        program_ = Program(block)
        return program_

    def get_indent(self) -> int:
        indent = 0
        # Monkey patch to prevent get_indent() from modifying indents such that other blocks can't see the changes
        token_index = self.token_index
        while self.match(TokenType.NEWLINE, False, False):
            pass
        while self.match(TokenType.WHITESPACE, False, False):
            indent += 1
            while self.match(TokenType.NEWLINE, False, False):
                indent = 0
        self.token_index = token_index
        self.current_token = self.tokens[token_index]
        return indent

    def block(self, prev_indent: int) -> Block | None:
        indent = self.get_indent()
        if indent <= prev_indent:
            self.raise_syntax_error("Expected an indented block")
        self.block_id += 1
        block_id_buffer = self.block_id
        statements: list[StatementType] = []
        statement = self.statement(indent)
        while statement is not None:
            statements.append(statement)
            new_indent = self.get_indent()
            if new_indent < indent:
                break
            statement = self.statement(indent)
        if not statements:
            self.block_id -= 1
            return None

        block_ = Block(statements, block_id_buffer, indent)
        return block_

    def match(
        self, token_type: TokenType, ignore_newline=True, ignore_whitespace=True
    ) -> bool:
        if self.token_index > len(self.tokens):
            return False
        self.token_index += 1
        self.current_token = self.tokens[self.token_index]
        matched = False
        if (
            self.current_token.type == TokenType.COMMENT
            or (ignore_newline and self.current_token.type == TokenType.NEWLINE)
            or (ignore_whitespace and self.current_token.type == TokenType.WHITESPACE)
        ):
            matched = self.match(token_type)

        else:
            matched = self.current_token.type == token_type
        if matched:
            return True
        self.token_index -= 1
        self.current_token = self.tokens[self.token_index]
        return False

    def generic_statement(
        self, token_type: TokenType, string_repr: str
    ) -> GenericStatement | None:
        if not self.match(token_type):
            return None
        stmt = GenericStatement(self.current_token, string_repr)
        return stmt

    def statement(self, indent: int) -> StatementType | None:
        statement = (
            self.generic_statement(TokenType.BREAK, "BREAK")
            or self.generic_statement(TokenType.CONTINUE, "CONTINUE")
            or self.generic_statement(TokenType.PASS, "PASS")
            or self.generic_statement(TokenType.COMMENT, "COMMENT")
            or self.assignment_statement()
            or self.while_statement_block(indent)
            or self.if_statement_block(indent)
        )
        return statement

    def assignment_statement(self) -> AssignmentStatement | None:
        if not self.match(TokenType.IDENTIFIER):
            return None
        identifier = self.current_token
        if not self.match(TokenType.ASSIGN):
            self.raise_syntax_error("Expected assignment operator")

        expression = self.expression()
        if expression is None:
            self.raise_syntax_error("Expected expression")
        stmt = AssignmentStatement(identifier, expression)
        return stmt

    def control_flow_stmt_block(
        self, token_type: TokenType, indent: int, has_expression=True
    ) -> ControlFlowStmtBlock | None:
        if not self.match(token_type):
            return None
        token = self.current_token
        expression: Expression | None = None
        if has_expression:
            expression = self.expression()
            if expression is None:
                self.raise_syntax_error("Expected expression")
        if not self.match(TokenType.COLON):
            self.raise_syntax_error("Expected colon")
        if not self.match(TokenType.NEWLINE, False):
            self.raise_syntax_error("Expected newline")
        block = self.block(indent)
        if block is None:
            self.raise_syntax_error("Expected code block")
        stmt_block = ControlFlowStmtBlock(token, expression, block)
        return stmt_block

    def if_statement_block(self, indent: int) -> IfStatementBlock | None:
        if_stmt_block = self.control_flow_stmt_block(TokenType.IF, indent)
        if if_stmt_block is None:
            return None
        elifs: list[ControlFlowStmtBlock] = []
        elif_stmt_block = self.control_flow_stmt_block(TokenType.ELIF, indent)
        while elif_stmt_block is not None:
            elifs.append(elif_stmt_block)
            elif_stmt_block = self.control_flow_stmt_block(TokenType.ELIF, indent)
        else_stmt_block = self.control_flow_stmt_block(TokenType.ELSE, indent, False)
        statement_block = IfStatementBlock(if_stmt_block, elifs, else_stmt_block)
        return statement_block

    def while_statement_block(self, indent: int) -> ControlFlowStmtBlock | None:
        stmt_block = self.control_flow_stmt_block(TokenType.WHILE, indent)
        return stmt_block

    def factor(self) -> bool:
        return (
            self.match(TokenType.BOOL_TRUE)
            or self.match(TokenType.BOOL_FALSE)
            or self.match(TokenType.IDENTIFIER)
            or self.match(TokenType.STRING)
            or self.match(TokenType.INTEGER)
            or self.match(TokenType.FLOAT)
        )

    def expression(self) -> Expression | None:
        def match_ops() -> bool:
            return (
                self.match(TokenType.OR)
                or self.match(TokenType.AND)
                or self.match(TokenType.NOT)
                or self.match(TokenType.DIVIDE)
                or self.match(TokenType.MULTIPLY)
                or self.match(TokenType.ADD)
                or self.match(TokenType.SUBTRACT)
                or self.match(TokenType.EQUAL)
                or self.match(TokenType.NOT_EQUAL)
                or self.match(TokenType.MODULUS)
                or self.match(TokenType.GREATER_THAN)
                or self.match(TokenType.LESS_THAN)
                or self.match(TokenType.GREATER_THAN_OR_EQUAL)
                or self.match(TokenType.LESS_THAN_OR_EQUAL)
            )

        left_operand: Expression | Token
        if self.match(TokenType.LPAREN):
            expression = self.expression()
            if expression is None:
                self.raise_syntax_error("Expected expression")
            left_operand = expression
            if not self.match(TokenType.RPAREN):
                self.raise_syntax_error("Expected closing paranthesis")
        else:
            if not self.factor():
                return None
            left_operand = self.current_token
        operator = None
        right_operand = None
        if match_ops():
            operator = self.current_token
            right_operand = self.expression()
            if right_operand is None:
                self.raise_syntax_error("Expected expression")
        expression = Expression(left_operand, operator, right_operand)
        return expression
