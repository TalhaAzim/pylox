from abc import ABC, abstractmethod

class LoxCallable(ABC):

    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def call(self, interpreter: 'Interpreter', arguments: list[object]) -> object:
        raise NotImplementedError
    