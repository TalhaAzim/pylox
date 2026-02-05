from loxcallable import LoxCallable
from loxfunction import LoxFunction
from loxinstance import LoxInstance

class LoxClass(LoxCallable):

    def __init__(self, name: str, methods: dict[str, LoxFunction]) -> None:
        self.name = name
        self.methods = methods
    
    def find_method(self, name: str) -> LoxFunction:
        if name in self.methods:
            return self.methods[name]
        return None
    
    def __str__(self) -> str:
        return self.name
    
    def call(self, interpreter: 'Interpreter', arguments: list[object]) -> object:
        instance: LoxInstance = LoxInstance(self)
        return instance
    
    def arity(self) -> int:
        return 0