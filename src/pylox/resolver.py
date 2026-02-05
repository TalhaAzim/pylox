import expr, stmt
from interpreter import Interpreter
from token import Token
from enum import Enum

FunctionType = Enum("FunctionType", ["NONE", "FUNCTION"]) 

class Resolver(expr.Visitor, stmt.Visitor):

    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE
    
    def visit_block_stmt(self, statement: stmt.Block) -> None:
        self.begin_scope()
        self.resolve(statement.statements)
        self.end_scope()
        return None 
    
    def visit_class_stmt(self, statement: stmt.Class) -> None:
        self.declare(statement.name)
        self.declare(statement.name)
        return None
    
    def visit_expression_stmt(self, statement: stmt.Expression) -> None:
        self.resolve(statement.expression)
        return None

    def visit_function_stmt(self, statement: stmt.Function) -> None:
        self.declare(statement.name)
        self.define(statement.name)

        self.resolve_function(statement, FunctionType.FUNCTION)
        return None
    
    def visit_if_stmt(self, statement: stmt.If) -> None:
        self.resolve(statement.condition)
        self.resolve(statement.then_branch)
        if not statement.else_branch is None:
            self.resolve(statement.else_branch)
        return None
    
    def visit_print_stmt(self, statement: stmt.Print) -> None:
        self.resolve(statement.expression)
        return None
    
    def visit_return_stmt(self, statement: stmt.Return) -> None:
        if self.current_function == FunctionType.NONE:
            from __init__ import Pylox # TODO: fix circular imports
            Pylox.error(statement.keyword, "Can't return from top-level code.")

        if not statement.value is None:
            self.resolve(statement.value)
        return None
    
    def resolve(self, statement: list[stmt.Stmt] | stmt.Stmt | expr.Expr) -> None:
        
        if type(statement) is list:
            for s in statement:
                self.resolve(s)
        else:
            statement.accept(self) # It's all about that self acceptance.
    
    def resolve_function(self, function: stmt.Function, fn_type: FunctionType) -> None:
        enclosing_function: FunctionType = self.current_function
        self.current_function = fn_type
        
        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self) -> None:
        self.scopes.append({})
    
    def end_scope(self) -> None:
        self.scopes.pop()
    
    def visit_var_stmt(self, statement: stmt.Var) -> None:
        self.declare(statement.name)
        if statement.initializer is not None:
            self.resolve(statement.initializer)
        self.define(statement.name)
        return None

    def visit_while_stmt(self, statement: stmt.While) -> None:
        self.resolve(statement.condition)
        self.resolve(statement.body)
        return None
    
    def declare(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return None
        
        scope = self.scopes[-1]
        if name.lexeme in scope:
            from __init__ import Pylox # TODO: Fix circular import issue
            Pylox.error(name, "Already a variable with this name in this scope")

        scope[name.lexeme] = False
    
    def define(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return None
        
        self.scopes[-1][name.lexeme] = True
    
    def visit_variable_expr(self, expression: expr.Variable) -> None:
        if len(self.scopes) > 0 and self.scopes[-1].get(expression.name.lexeme) == False:
            from __init__ import Pylox
            Pylox.error(expression.name, "Can't read local variable in it's own initializer.")
        
        self.resolve_local(expression, expression.name)
        return None
    
    def resolve_local(self, expression: expr.Expr, name: Token) -> None:
        index: int = len(self.scopes) - 1

        while index >= 0:
            if name.lexeme in self.scopes[index]:
                self.interpreter.resolve(expression, len(self.scopes) - 1 - index)
                return
            index -= 1
    
    def visit_assign_expr(self, expression: expr.Assign) -> None:
        self.resolve(expression.value)
        self.resolve_local(expression, expression.name)
        return None
    
    def visit_binary_expr(self, expression: expr.Binary) -> None:
        self.resolve(expression.left)
        self.resolve(expression.right)
        return None
    
    def visit_call_expr(self, expression: expr.Call) -> None:
        self.resolve(expression.callee)
        
        for argument in expression.arguments:
            self.resolve(argument)
        
        return None
    
    def visit_get_expr(self, expression: expr.Get) -> None:
        self.resolve(expression.objekt)
        return None

    def visit_grouping_expr(self, expression: expr.Grouping) -> None:
        self.resolve(expression.expression)
        return None
    
    def visit_literal_expr(self, expression: expr.Literal) -> None:
        return None
    
    def visit_logical_expr(self, expression: expr.Logical) -> None:
        self.resolve(expression.left)
        self.resolve(expression.right)
        return None
    
    def visit_set_expr(self, expression: expr.Set) -> None:
        self.resolve(expression.value)
        self.resolve(expression.objekt)        
        return None

    def visit_unary_expr(self, expression: expr.Unary) -> None:
        self.resolve(expression.right)
        return None
