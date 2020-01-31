from typing import Callable
from .handler import Handler


def handle(event: str) -> Callable[[callable], callable]:
    def decorate(func: callable) -> callable:
        Handler.get()[event] = func
        return func
    return decorate
