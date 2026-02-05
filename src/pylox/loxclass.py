from loxcallable import LoxCallable
from loxinstance import LoxInstance

class LoxClass(LoxCallable):

    def __init__(self, name: str, environment: object = None) -> None:
        self.name = name
    
    def __str__(self) -> str:
        return self.name
    
    def call(self, interpreter: 'Interpreter', arguments: list[object]) -> object:
        instance: LoxInstance = LoxInstance(self)
        return instance
    
    def arity(self) -> int:
        return 0