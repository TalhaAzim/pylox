from loxcallable import LoxCallable
from loxfunction import LoxFunction
from loxinstance import LoxInstance

class LoxClass(LoxCallable):

    def __init__(self, name: str, superclass: 'LoxClass', methods: dict[str, LoxFunction]) -> None:
        self.name = name
        self.methods = methods
        self.superclass = superclass
    
    def find_method(self, name: str) -> LoxFunction | None:
        if name in self.methods:
            return self.methods[name]

        if self.superclass is not None:
            return self.superclass.find_method(name)
    
        return None

    def __str__(self) -> str:
        return self.name
    
    def call(self, interpreter: 'Interpreter', arguments: list[object]) -> object:
        instance: LoxInstance = LoxInstance(self)
        initializer: LoxFunction = self.find_method("init")
        
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def arity(self) -> int:
        initializer: LoxFunction = self.find_method("init")
        return 0 if initializer is None else initializer.arity()
