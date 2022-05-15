from concurrent.futures import Future

from dto.task_request import TaskRequest
from processor.communicator import Communicator


class OffLoader:

    def __init__(self, communicator: Communicator, foreign_entity_name: str, impl_signature: str,
                 foreign_entity_address: str):
        self.__communicator = communicator
        self.__foreign_entity_name = foreign_entity_name
        self.__impl_signature = impl_signature
        self.__communicator.register_sender(foreign_entity_name, foreign_entity_address)

    def offload_task(self, task_request: TaskRequest):

        token_id = self.__impl_signature + "::" + task_request.function_signature + "::" + "sdsdsdsd"

        task_delegation_response = Future()

        def listener(response_type=None, receive_message=None):
            if response_type is None:
                task_delegation_response.done()
            else:
                task_delegation_response.set_result(receive_message)
                task_delegation_response.done()

        self.__communicator.register_reply_listener(token_id, listener)

        self.__communicator.send_request(self.__foreign_entity_name, token_id, task_request.argument_list)

        return task_delegation_response
