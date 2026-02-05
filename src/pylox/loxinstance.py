
import runtimeerror

class LoxInstance:

    def __init__(self, klass: 'LoxClass') -> None: # TODO: circular import; loxclass imports loxinstance imports loxclass ...
        self.klass: 'LoxClass' = klass # What is this? Mortal Kombat?
        self.fields: dict[str, object] = {}
    
    def get(self, name: 'Token') -> object:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        raise runtimeerror.RuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: 'Token', value: object) -> None:
        self.fields[name.lexeme] = value
    
    def __str__(self) -> str:
        return f"{self.klass.name} instance"