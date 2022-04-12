import inspect
from abc import ABCMeta
from types import SimpleNamespace


class ForeignInterfaceHandler:

    @staticmethod
    def wire_foreign_impl(x: ABCMeta):
        method_list = [func for func in dir(x) if callable(getattr(x, func)) and not func.startswith("__")]
        impl = SimpleNamespace()
        for method in method_list:
            func_obj = getattr(x, method)
            if not getattr(func_obj, '__isabstractmethod__', False):
                continue
            def func(*args):
                for arg in args:
                    print(arg)

            print(func_obj.__annotations__["return"])
            setattr(impl, method, func)
        return impl
