import typing
from concurrent.futures import ALL_COMPLETED, wait

from concurrency.thread_handler import ThreadHandler
from marker.foreign_service_impl import ForeignServiceImpl
from model.addressbook_pb2 import Person, AddressBook
from processor.communicator import Communicator


class ServiceHandler:

    __service_impl_map = {}

    def __init__(self, communicator: Communicator, thread_handler: ThreadHandler):
        self.__communicator = communicator
        self.__thread_pool_executor = thread_handler.initiate_service_thread_pool(1)
        communicator.register_receiver(["tcp://127.0.0.1:5555"], self.__listen)

    #     if (!configuration.getBindAddresses().isEmpty()) {
    #         this.executorService = threadHandler.initiateServiceThreadPool(configuration.getServiceParallelism());
    #         this.communicator.registerReceiver(configuration.getBindAddresses(), this::listen);
    #     }
    #
    # }

    @staticmethod
    def register_new_service(service_impl: ForeignServiceImpl, service_impl_signature: str):

        service_meta_map = {}
        method_list = [func for func in dir(service_impl) if
                       callable(getattr(service_impl, func)) and not func.startswith("__")]
        for method in method_list:
            func_obj = getattr(service_impl, method)
            if not getattr(func_obj, '__is_foreign_impl__', False):
                continue
            foreign_execution_params = getattr(func_obj, '__foreign_execution_params__')

            service_meta_map[foreign_execution_params['function_signature']] = {
                'method': method,
                'meta_data': foreign_execution_params,
            }
        ServiceHandler.__service_impl_map[service_impl_signature] = {
            'instance': service_impl,
            'meta_map': service_meta_map
        }

    def __listen(self, method_sign, request_args):
        def __worker(signature, request_params):
            try:
                method_meta = signature.split("::")
                instance_date = ServiceHandler.__service_impl_map[method_meta[0]]
                function_internals = instance_date['meta_map'][method_meta[1]]
                function_meta_data = function_internals['meta_data']
                input_params = []
                counter = 0
                for input_param_type in function_meta_data["input_param_types"]:
                    param = input_param_type()
                    param.ParseFromString(request_params[counter])
                    input_params.append(param)
                    counter = counter + 1
                response = getattr(instance_date['instance'], function_internals['method'])(*input_params)
                if function_meta_data["is_async"]:
                    wait([response], return_when=ALL_COMPLETED)
                if function_meta_data["return_type"]:
                    self.__communicator.send_reply(method_sign, response.SerializeToString())
                else:
                    self.__communicator.send_reply(method_sign)
            except Exception as e:
                print(e)

        self.__thread_pool_executor.submit(__worker, method_sign, request_args)
