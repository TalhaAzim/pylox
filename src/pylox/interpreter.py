import expr
import stmt
from token import TokenType, Token
from __init__ import Pylox
import runtimeerror
import environment

class Interpreter(expr.Visitor, stmt.Visitor):

    def __init__(self) -> None:
        self.environment = environment.Environment()

    def evaluate(self, expression: expr.Expr) -> object:
        return expression.accept(self)
    
    def execute(self, statement: stmt.Stmt) -> None:
        statement.accept(self)
    
    def execute_block(self, statements: list[stmt.Stmt], environment: environment.Environment) -> None:
        previous: environment.Environment = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def visit_block_stmt(self, statement: stmt.Block) -> None:
        self.execute_block(statement.statements, environment.Environment(self.environment))
        return None
    
    def visit_expression_stmt(self, statement: stmt.Expression) -> None:
        self.evaluate(statement.expression)
        return None
    
    def visit_if_stmt(self, statement: stmt.If) -> None:
        if self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute(statement.else_branch)
        
        return None
    
    def visit_print_stmt(self, statement: stmt.Print) -> None:
        value: object = self.evaluate(statement.expression)
        print(self.stringify(value))
        return None
    
    def visit_var_stmt(self, statement: stmt.Var) -> None:
        value: object = None
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)
        
        self.environment.define(statement.name.lexeme, value)
        return None
    
    def visit_while_stmt(self, statement: stmt.While) -> None:
        while self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.body)
        return None

    def visit_assign_expr(self, expression: expr.Assign) -> object:
        value: object = self.evaluate(expression.value)
        self.environment.assign(expression.name, value)
        return value
    
    def visit_literal_expr(self, expression: expr.Literal) -> object:
        return expression.value
    
    def visit_logical_expr(self, expression: expr.Logical) -> object:
        left: object = self.evaluate(expression.left)

        if expression.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        
        return self.evaluate(expression.right)
    
    def visit_grouping_expr(self, expression: expr.Grouping) -> object:
        return self.evaluate(expression.expression)
    
    def visit_unary_expr(self, expression: expr.Unary) -> object:
        right: object = self.evaluate(expression.right)
        self.check_number_operand(expression.operator, right)

        match expression.operator.tokentype:
            case TokenType.MINUS:
                return -right
            case TokenType.BANG:
                # if it's not tight
                return not self.is_truthy(right)
        
        return None
    
    def visit_variable_expr(self, expression: expr.Variable) -> None:
        return self.environment.get(expression.name)

    def is_truthy(self, obj: object) -> bool:
        if obj is None:
            return False
        if (isinstance(obj, bool)):
            return obj
        return True
    
    def visit_binary_expr(self, expression: expr.Binary) -> object:
        left: object = self.evaluate(expression.left)
        right: object = self.evaluate(expression.right)

        match expression.operator.tokentype:
            case TokenType.GREATER:
                self.check_number_operands(expression.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expression.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(expression.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expression.operator, left, right)
                return left <= right
            case TokenType.MINUS:
                self.check_number_operands(expression.operator, left, right)
                return left - right
            case TokenType.PLUS:
                print(f"Adding {left} and {right}")
                if (isinstance(left, float) and isinstance(right, float)):
                    return left + right
                if (isinstance(left, str) and isinstance(right, str)):
                    return left + right # Python overloads + anyway
                raise runtimeerror.RuntimeError(expression.operator, "Operands must be two numbers or two strings.")
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

        # TODO: verify if the statement below is consistent with intended design
        return a == b

    def stringify(self, obj: object) -> str:
        if obj is None:
            return "null"

        if isinstance(obj, float):
            text: str = str(obj)
            if text.endswith(".0"):
                text = text[:-2]

        return str(obj)

    def check_number_operand(self, operator: Token, operand: object) -> None:
        if (isinstance(operand, float)):
            return None
        raise runtimeerror.RuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: object, right: object) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return None
        raise runtimeerror.RuntimeError(operator, "Operands must be numbers.")

    def interpret(self, statements: list[stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            Pylox.runtime_error(error)
