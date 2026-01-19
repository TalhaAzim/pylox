from abc import ABC, abstractmethod
from token import Token

class Expr(ABC):

    @abstractmethod
    def accept(self, visitor: 'Visitor') -> None:
        raise NotImplementedError

class Assign(Expr):

    def __init__(self, name: 'Token', value: 'Expr') -> None:
        self.name: 'Token' = name
        self.value: 'Expr' = value

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_assign_expr(self)

class Binary(Expr):

    def __init__(self, left: 'Expr', operator: Token, right: 'Expr') -> None:
        self.left: 'Expr' = left
        self.operator: Token = operator
        self.right: 'Expr' = right

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_binary_expr(self)

class Call(Expr):

    def __init__(self, callee: 'Expr', paren: 'Token', arguments: 'list[Expr]') -> None:
        self.callee: 'Expr' = callee
        self.paren: 'Token' = paren
        self.arguments: 'list[Expr]' = arguments

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_call_expr(self)

class Grouping(Expr):

    def __init__(self, expression: 'Expr') -> None:
        self.expression: 'Expr' = expression

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_grouping_expr(self)

class Literal(Expr):

    def __init__(self, value: 'object') -> None:
        self.value: 'object' = value

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_literal_expr(self)

class Logical(Expr):

    def __init__(self, left: 'Expr', operator: 'Token', right: 'Expr') -> None:
        self.left: 'Expr' = left
        self.operator: 'Token' = operator
        self.right: 'Expr' = right

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_logical_expr(self)

class Unary(Expr):

    def __init__(self, operator: 'Token', right: 'Expr') -> None:
        self.operator: 'Token' = operator
        self.right: 'Expr' = right

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_unary_expr(self)

class Variable(Expr):

    def __init__(self, name: 'Token') -> None:
        self.name: 'Token' = name

    def accept(self, visitor: 'Visitor') -> None:
        return visitor.visit_variable_expr(self)

class Visitor(ABC):

    @abstractmethod
    def visit_assign_expr(self, expr: 'Assign') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_binary_expr(self, expr: 'Binary') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_call_expr(self, expr: 'Call') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_grouping_expr(self, expr: 'Grouping') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_literal_expr(self, expr: 'Literal') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_logical_expr(self, expr: 'Logical') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_unary_expr(self, expr: 'Unary') -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_variable_expr(self, expr: 'Variable') -> None:
        raise NotImplementedError

