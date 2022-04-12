from abc import ABC, abstractmethod

class SlaveInterface(ABC):

    @abstractmethod
    def get_person(self, purchase) -> int:
        pass

    @abstractmethod
    def get_async_person(self, sale) -> int:
        pass