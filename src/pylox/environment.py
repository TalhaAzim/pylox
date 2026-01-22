from token import Token
import runtimeerror

class Environment():

    def __init__(self, enclosing: 'Environment' = None) -> None:
        self.enclosing = enclosing
        self.values = {}

    def define(self, name: str, value: object) -> None:
        self.values[name] = value
    
    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        if self.enclosing:
            return self.enclosing.get(name)

        raise runtimeerror.RuntimeError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return None
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return None
        
        raise runtimeerror.RuntimeError(name, "Undefined variable '" + name.lexeme + "'.")