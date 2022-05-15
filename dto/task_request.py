from dataclasses import dataclass


@dataclass
class TaskRequest:
    argument_list: list
    function_signature: str
