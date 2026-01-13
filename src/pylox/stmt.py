from abc import ABC, abstractmethod
from token import Token

class Stmt(ABC):

    @abstractmethod
    def accept(self, visitor: 'Visitor') -> None:
        raise NotImplementedError

class Block(Stmt):

    def __init__(self, statements: 'list[Stmt]') -> None:
        self.statements: 'list[Stmt]' = statements

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_block_stmt(self)

class Expression(Stmt):

    def __init__(self, expression: 'Expr') -> None:
        self.expression: 'Expr' = expression

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_expression_stmt(self)

class Print(Stmt):

    def __init__(self, expression: 'Expr') -> None:
        self.expression: 'Expr' = expression

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_print_stmt(self)

class Var(Stmt):

    def __init__(self, name: 'Token', initializer: 'Expr') -> None:
        self.name: 'Token' = name
        self.initializer: 'Expr' = initializer

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_var_stmt(self)

class Visitor(ABC):

    @abstractmethod
    def visit_block_stmt(self, stmt: 'Block') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_expression_stmt(self, stmt: 'Expression') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_print_stmt(self, stmt: 'Print') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_var_stmt(self, stmt: 'Var') -> None:
        raise NotImplementedError

