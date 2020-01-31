from typing import Any, Dict, AnyStr

class Context():
    def __init__(self: Context) -> None:
        self._params: Dict[str, AnyStr] = {}

    async def load(self: Context, params: Dict[str, AnyStr]) -> None:
        self._params = params

    def __getattribute__(self: Context, attribute: str) -> Any:
        if attribute in self._params:
            return self._params[attribute]
        raise KeyError(attribute)
