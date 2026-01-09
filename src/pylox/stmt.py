from abc import ABC, abstractmethod
from token import Token

class Stmt(ABC):

    @abstractmethod
    def accept(self, visitor: 'Visitor') -> None:
        raise NotImplementedError

class Expression(Stmt):

    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_expression_stmt(self)

class Print(Stmt):

    def __init__(self, expression: Expr) -> None:
        self.expression: Expr = expression

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_print_stmt(self)

class Visitor(ABC):

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> None:
        raise NotImplementedError

