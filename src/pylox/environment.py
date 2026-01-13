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
            return values[name.lexeme]
        
        if enclosing:
            return enclosing[name]

        raise runtimeerror.RuntimeError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def assign(name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return None
        
        if enclosing:
            enclosing.assign(name, value)
            return None
        
        raise runtimeerror.RuntimeError(name, "Undefined variable '" + name.lexeme + "'.")