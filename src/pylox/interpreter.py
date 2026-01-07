from expr import *

class Interpreter(Visitor):

    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value
    
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr.right)

        match expr.operator.tokentype:
            case TokenType.MINUS:
                return -right
            case TokenType.BANG:
                # if it's not tight
                return self.is_truthy(right)
        
        return None
    
    def is_truthy(self, obj: object) -> bool:
        if obj is None:
            return False
        if (isinstance(obj, bool)):
            return obj
        return True