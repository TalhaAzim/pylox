from expr import *

class Interpreter(Visitor):

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value