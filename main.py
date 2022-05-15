# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import random
import sys
import time

from model import addressbook_pb2
from processor.foreign_interface_handler import ForeignInterfaceHandler
from slave_interface import SlaveInterface


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    slave_interface = ForeignInterfaceHandler.wire_foreign_impl(SlaveInterface)
    person = addressbook_pb2.Person()
    person.id = 1234
    person.name = "John Doe"
    person.email = "jdoe@example.com"
    print(person)
    slave_interface.get_person(person)
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi("jooo")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/




