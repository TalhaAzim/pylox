from abc import ABC, abstractmethod
from token import Token

class Expr(ABC):
    pass


class Binary(Expr):

    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        this.left: Expr = left
        this.operator: Token = operator
        this.right: Expr = right

class Grouping(Expr):

    def __init__(self, expression: Expr) -> None:
        this.expression: Expr = expression

class Literal(Expr):

    def __init__(self, value: object) -> None:
        this.value: object = value

class Unary(Expr):

    def __init__(self, operator: Token, right: Expr) -> None:
        this.operator: Token = operator
        this.right: Expr = right

