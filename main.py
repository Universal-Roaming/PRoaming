from model import addressbook_pb2
from processor.foreign_interface_handler import ForeignInterfaceHandler
from slave_impl import SlaveImpl
from slave_interface import SlaveInterface

if __name__ == '__main__':
    # slave_interface = ForeignInterfaceHandler.wire_foreign_impl(SlaveInterface, "service-signature-1",
    #                                                             "dataCollectionService")
    # addressbook = addressbook_pb2.AddressBook()
    # person = addressbook.people.add()
    # person.id = 1234
    # person.name = "John Doe"
    # person.email = "jdoe@example.com"
    #
    # addressbook.people[0].name =addressbook.people[0].name +"updated"
    #
    # person2 = addressbook.people[0]
    # print(person2)
    slave_impl = SlaveImpl()
    ForeignInterfaceHandler.create_foreign_service_impl(slave_impl, "dataCollectionService")
    # person_data = slave_interface.get_person(addressbook)
    # print(person_data.name)




