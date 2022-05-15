from concurrent.futures import wait
from importlib import import_module
from types import SimpleNamespace
import typing

from dto.task_request import TaskRequest
from marker.foreign_service import ForeignService
from processor.communicator import Communicator
from processor.offloader import OffLoader


class ForeignInterfaceHandler:
    # __communicator = Communicator(False)
    # __offloader = OffLoader(__communicator,'test','sdsds','sdsdsdsd')

    @staticmethod
    def wire_foreign_impl(x: typing.Type[ForeignService]):
        method_list = [func for func in dir(x) if callable(getattr(x, func)) and not func.startswith("__")]
        impl = SimpleNamespace()
        for method in method_list:
            func_obj = getattr(x, method)
            if not getattr(func_obj, '__is_foreign__', False):
                continue
            foreign_execution_params = getattr(func_obj, '__foreign_execution_params__')
            print(foreign_execution_params)
            def overloaded_func(*args):
                serialized_argument_list = []
                for arg in args:
                    person_class = foreign_execution_params["return_type"]()
                    person_data = arg.SerializeToString()
                    person_class.ParseFromString(person_data)
                    print(person_class)
                    serialized_argument_list.append(arg.SerializeToString())

                task_request = TaskRequest(
                    argument_list=serialized_argument_list,
                    function_signature=foreign_execution_params['function_signature'],
                )

                # task_delegation_response = ForeignInterfaceHandler.__offloader.offload_task(task_request)
                #
                # if foreign_execution_params['async']:
                # # valid
                # else:
                #     completed_future = wait([task_delegation_response])


            # print(func_obj.__annotations__["return"])
            setattr(impl, method, overloaded_func)
        return impl
