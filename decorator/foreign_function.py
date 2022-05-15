def foreign_function(function_signature, time_out=None, return_type=None, is_async=False):
    def func_wrapper(func):
        func.__is_foreign__ = True
        func.__foreign_execution_params__ = {
            "function_signature": function_signature,
            "time_out": time_out,
            "return_type": return_type,
            "is_async": is_async
        }
        return func

    return func_wrapper
