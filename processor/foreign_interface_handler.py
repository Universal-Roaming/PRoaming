from concurrent.futures import wait, ALL_COMPLETED
from types import SimpleNamespace
import typing

from dto.task_request import TaskRequest
from marker.foreign_service_impl import ForeignServiceImpl
from marker.foreign_service import ForeignService
from processor.communicator import Communicator
from processor.offloader import OffLoader
from concurrency.thread_handler import ThreadHandler
from processor.service_handler import ServiceHandler


class ForeignInterfaceHandler:
    __thread_handler = ThreadHandler()
    __communicator = Communicator(__thread_handler, True)
    __service_handler = ServiceHandler(__communicator, __thread_handler)
    __service_map = {}

    @staticmethod
    def wire_foreign_impl(foreign_service: typing.Type[ForeignService], service_signature: str, impl_signature: str):
        if service_signature+"_"+impl_signature in ForeignInterfaceHandler.__service_map:
            return ForeignInterfaceHandler.__service_map[service_signature+"_"+impl_signature]
        __offloader = OffLoader(ForeignInterfaceHandler.__communicator, service_signature, impl_signature,
                                "tcp://127.0.0.1:5555")
        method_list = [func for func in dir(foreign_service) if callable(getattr(foreign_service, func)) and not func.startswith("__")]
        impl = SimpleNamespace()
        for method in method_list:
            func_obj = getattr(foreign_service, method)
            if not getattr(func_obj, '__is_foreign__', False):
                continue
            foreign_execution_params = getattr(func_obj, '__foreign_execution_params__')

            def overloaded_func(*args):
                serialized_argument_list = []
                for arg in args:
                    serialized_argument_list.append(arg.SerializeToString())

                task_request = TaskRequest(
                    argument_list=serialized_argument_list,
                    function_signature=foreign_execution_params['function_signature'],
                )

                task_delegation_response = __offloader.offload_task(task_request)

                def mapping_function(data):
                    if foreign_execution_params["return_type"] is None:
                        return None
                    else:
                        return_instance = foreign_execution_params["return_type"]()
                        return_instance.ParseFromString(data.result())
                        return return_instance

                if foreign_execution_params['is_async']:
                    task_delegation_response.add_done_callback(mapping_function)
                    return task_delegation_response

                wait([task_delegation_response], return_when=ALL_COMPLETED)

                return mapping_function(task_delegation_response)

            setattr(impl, method, overloaded_func)
        ForeignInterfaceHandler.__service_map[service_signature + "_" + impl_signature] = impl
        return impl

    @staticmethod
    def create_foreign_service_impl(foreign_service_impl: ForeignServiceImpl, service_impl_signature: str):
        ForeignInterfaceHandler.__service_handler.register_new_service(foreign_service_impl, service_impl_signature)