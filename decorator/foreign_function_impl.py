import typing


def foreign_function_impl(function_signature, time_out=None, is_async=False):
    def func_wrapper(func):
        func.__is_foreign_impl__ = True
        input_param_types = []
        return_type = None
        for key, value in func.__annotations__.items():
            if key == "return":
                if isinstance(value, typing._GenericAlias) and value.__origin__.__name__ == 'Awaitable':
                    return_type = value.__args__[0]
                else:
                    return_type = value
            else:
                input_param_types.append(value)

        func.__foreign_execution_params__ = {
            "function_signature": function_signature,
            "time_out": time_out,
            "return_type": return_type,
            "is_async": is_async,
            'input_param_types': input_param_types
        }
        return func

    return func_wrapper
