from expr import *
from __init__ import Pylox
import runtimeerror

class Interpreter(Visitor):

    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value
    
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: Unary) -> object:
        self.check_number_operand(expr.operator, right)
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
    
    def visit_binary_expr(self, expr: bool) -> object:
        left: object = expr.left
        right: object = expr.right

        match obj.operator.tokentype:
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.PLUS:
                if (isinstance(left, float) and isinstance(right, float)):
                    return left + right
                if (isinstance(left, str) and isinstance(right, str)):
                    return left + right # Python overloads + anyway
                raise runtimeerror.RuntimeError(expr.operator, "Operands must be two numbers or two strings.")
            case TokenType.SLASH:
                return left / right
            case TokenType.STAR:
                return left * right
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            
        return None

        def is_equal(self, a: object, b: object) -> bool:
            if a is None and b is None:
                return True
            if a is None:
                return False
            
            # TODO: verify if the statement below consistently with inteded design
            return a == b
    
        def check_number_operand(self, operator: Token, operand: object) -> None:
            if (isinstance(operand, float)):
                return None
            raise runtimeerror.RuntimeError(operator, "Operand must be a number.")
        
        def check_number_operands(self, operator: Token, left: object, right: object) -> None:
            if ininstance(left, float) and isinstance(right, float):
                return None
            raise runtimeerror.RuntimeError(operator, "Operands must be numbers.")
        
        def interpret(self, expression: Expr) -> None:
            try:
                value: object = self.evaluate(expression)
                print(self.stringify(value))
            except RuntimeError as error:
                Lox.runtime_error(error)