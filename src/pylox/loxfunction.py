import loxcallable
import environment

class LoxFunction(loxcallable.LoxCallable):

    def __init__(self, declaration: 'stmt.Function'):
        self.declaration = declaration
    
    def call(self, interpreter: 'Interpreter', arguments: list[object]) -> object:
        environment: environment.Environment = environment.Environment()

        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, argument)
        
        interpreter.execute_block(declaration.body, environment)
        return None
    
    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
