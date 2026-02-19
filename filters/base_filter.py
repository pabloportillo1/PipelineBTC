from abc import ABC, abstractmethod


class BaseFilter(ABC):


    @abstractmethod
    def process(self, transaction: dict) -> dict:

        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
