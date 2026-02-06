import loxcallable
from environment import Environment
from returnexception import ReturnException
from loxinstance import LoxInstance

class LoxFunction(loxcallable.LoxCallable):

    def __init__(self, declaration: 'stmt.Function', closure: Environment, is_initializer: bool) -> None:
        self.closure = closure
        self.declaration = declaration
        self.is_initializer = is_initializer
    
    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)
    
    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: 'Interpreter', arguments: list[object]) -> object:
        environment: Environment = Environment(self.closure)

        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, argument)
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as exception:
            return self.closure.get_at(0, "this") if self.is_initializer else exception.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None
    
    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
