import time
from concurrent.futures import ThreadPoolExecutor

import zmq

from concurrency.thread_handler import ThreadHandler
from util.constant import COMMUNICATOR_WAIT_TIME


class Communicator:

    __reply_listener_map = dict()
    __completed_task_queue = list()
    __sent_task_map = dict()
    __pending_task_map = dict()
    __concurrent_task_queue = list()
    __socket_map = dict()
    __receivers = list()

    __serviceListener = None

    __context = zmq.Context()

    def __communication_handler(self):
        while True:
            com_initiate_time_stamp = time.time()
            request_task_queue_size = len(self.__concurrent_task_queue)
            for x in range(request_task_queue_size):
                message = self.__concurrent_task_queue.pop(0)

                task_id = message['task_id']

                request_token_id = message['data']['token_id']

                serialized_arrays = message['data']['bytes']

                if task_id in self.__sent_task_map:
                    self.__sent_task_map[task_id][request_token_id] = serialized_arrays
                else:
                    self.__sent_task_map[task_id] = {
                        request_token_id: serialized_arrays
                    }

                send_packets = [bytearray(request_token_id.encode())]
                for serialized_array in serialized_arrays:
                    send_packets.append(bytearray(serialized_array))
                self.__socket_map[task_id].send_multipart(send_packets)

            for key, value in self.__socket_map.items():
                try:
                    in_msg = value.recv_multipart(zmq.NOBLOCK)
                    request_token_id = in_msg[0].decode()
                    if len(in_msg) > 1:
                        self.__reply_listener_map[request_token_id](True, in_msg[1])
                    else:
                        self.__reply_listener_map[request_token_id]()

                    del self.__reply_listener_map[request_token_id]
                    del self.__socket_map[key][request_token_id]

                except zmq.ZMQError as e:
                    if e.errno == zmq.EAGAIN:
                        pass
                    else:
                        raise

            for receiver in self.__receivers:
                for i in range(10):
                    try:
                        in_msg = receiver.recv_multipart(zmq.NOBLOCK)
                        caller_id = in_msg[0]
                        client_token_id = in_msg[1].decode()
                        request_args = []
                        if len(in_msg) > 2:
                            for x in range(2, len(in_msg)):
                                request_args.append(in_msg[x])
                        self.__serviceListener(client_token_id, request_args)
                        self.__pending_task_map[client_token_id] = caller_id
                    except zmq.ZMQError as e:
                        if e.errno == zmq.EAGAIN:
                            pass
                        else:
                            raise
                completed_task_queue_size = len(self.__completed_task_queue)

                for x in range(completed_task_queue_size):
                    completed_message = self.__completed_task_queue.pop(0)
                    client_token_id = completed_message['client_token_id']
                    send_packets = [self.__pending_task_map[client_token_id], bytearray(client_token_id.encode())]
                    if completed_message['data'] is not None:
                        send_packets.append(bytearray(completed_message['data']))
                    receiver.send_multipart(send_packets)
                    del self.__pending_task_map[client_token_id]

            com_completed_time_stamp = time.time()

            elapsed_time = com_completed_time_stamp - com_initiate_time_stamp

            if elapsed_time < COMMUNICATOR_WAIT_TIME:
                time.sleep(COMMUNICATOR_WAIT_TIME - elapsed_time)

    def __init__(self, thread_handler: ThreadHandler, is_independent_server):
        thread_handler.initiate_task_routine(not is_independent_server, self.__communication_handler)

    def register_sender(self, task_id, connection_address):
        requester = self.__context.socket(zmq.DEALER)
        requester.connect(connection_address)
        self.__socket_map[task_id] = requester

    def register_receiver(self, bind_addresses, service_listener):
        for bind_address in bind_addresses:
            receive_socket = self.__context.socket(zmq.ROUTER)
            receive_socket.bind(bind_address)
            self.__receivers.append(receive_socket)
        self.__serviceListener = service_listener

    def send_request(self, task_id, token_id, serialized_byte_arrays):
        self.__concurrent_task_queue.append(
            {'task_id': task_id, 'data': {'token_id': token_id, 'bytes': serialized_byte_arrays}}
        )

    def register_reply_listener(self, token_id, async_function):
        self.__reply_listener_map[token_id] = async_function

    def send_reply(self, token_id, serialized_byte_array=None):
        self.__completed_task_queue.append({'client_token_id': token_id, 'data': serialized_byte_array})
