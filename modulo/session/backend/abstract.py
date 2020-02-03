from typing import Dict, Any
from modulo.server import Context


class Abstract():
    async def load(self: Abstract) -> None:
        raise NotImplementedError()

    async def save(self: Abstract) -> None:
        raise NotImplementedError()

    def __init__(self: Abstract, key: str, context: Context) -> None:
        self._data: Dict[str, Any] = {}
        self._key = key
        self._context = Context

    def __getattr__(self: Abstract, key: str) -> Any:
        return self._data

    def __setattr__(self: Abstract, key: str, value: Any) -> None:
        self._data[key] = value
