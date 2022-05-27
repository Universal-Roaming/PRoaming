from abc import abstractmethod
from typing import Awaitable

from decorator.foreign_function import foreign_function
from marker.foreign_service import ForeignService
from model.addressbook_pb2 import Person, AddressBook


class SlaveInterface(ForeignService):

    @abstractmethod
    @foreign_function(function_signature='getPerson', is_async=False)
    def get_person(self, addressbook: AddressBook) -> Person:
        pass

    @abstractmethod
    @foreign_function(function_signature='getAsyncPerson', is_async=True)
    def get_async_person(self, addressbook: AddressBook) -> Awaitable[Person]:
        pass
