import loxcallable
from environment import Environment
from returnexception import ReturnException

class LoxFunction(loxcallable.LoxCallable):

    def __init__(self, declaration: 'stmt.Function', closure: Environment = None) -> None:
        self.closure = closure
        self.declaration = declaration
    
    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: 'Interpreter', arguments: list[object]) -> object:
        environment: Environment = Environment(self.closure)

        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, argument)
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as exception:
            return exception.value

        return None
    
    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
