from typing import Awaitable

from decorator.foreign_function_impl import foreign_function_impl
from marker.foreign_service_impl import ForeignServiceImpl
from model.addressbook_pb2 import Person, AddressBook


class SlaveImpl(ForeignServiceImpl):

    @foreign_function_impl(function_signature='getPerson', is_async=False)
    def get_person(self, addressbook: AddressBook) -> Person:
        addressbook.people[0].name = addressbook.people[0].name + "updated"
        return addressbook.people[0]

    @foreign_function_impl(function_signature='getAsyncPerson', is_async=True)
    def get_async_person(self, addressbook: AddressBook) -> Awaitable[Person]:
        addressbook.people[0].name = addressbook.people[0].name + "updated"
        return addressbook.people[0]
