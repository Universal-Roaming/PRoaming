from abc import abstractmethod, ABC
from concurrent.futures import Future
from typing import Union

from decorator.foreign_function import foreign_function
from marker.foreign_service import ForeignService
from model.addressbook_pb2 import Person


class SlaveInterface(ForeignService):
    @abstractmethod
    @foreign_function(function_signature='get_person', is_async=True, return_type=Person)
    def get_person(self, purchase):
        pass

    @abstractmethod
    def get_async_person(self, sale) -> int:
        pass
