from datetime import datetime
from typing import Callable

def get_current_year():

    return datetime.now().year
def call_method(_func:Callable,obj):
    if not callable(_func):
            raise Exception(f" The function {_func} its not a function")

    _func(obj)