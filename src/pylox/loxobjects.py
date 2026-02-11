from abc import ABC, abstractmethod
from environment import Environment
import runtimeerror
from returnexception import ReturnException


class LoxCallable(ABC):

    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def call(self, interpreter: 'Interpreter', arguments: list[object]) -> object:
        raise NotImplementedError

class LoxFunction(LoxCallable):

    def __init__(self, declaration: 'stmt.Function', closure: Environment, is_initializer: bool) -> None:
        self.closure = closure
        self.declaration = declaration
        self.is_initializer = is_initializer
    
    def bind(self, instance: 'LoxInstance') -> 'LoxFunction': # TODO: consider a separate class for method (vs function)
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

class LoxInstance:

    def __init__(self, klass: 'LoxClass') -> None: # TODO: circular import; loxclass imports loxinstance imports loxclass ...
        self.klass: 'LoxClass' = klass # What is this? Mortal Kombat?
        self.fields: dict[str, object] = {}
    
    def get(self, name: 'Token') -> object:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method: LoxFunction = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
    
        raise runtimeerror.RuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: 'Token', value: object) -> None:
        self.fields[name.lexeme] = value
    
    def __str__(self) -> str:
        return f"{self.klass.name} instance"
