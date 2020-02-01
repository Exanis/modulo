from typing import Dict, Any


class Abstract():
    async def load(self: Abstract) -> None:
        raise NotImplementedError()

    async def save(self: Abstract) -> None:
        raise NotImplementedError()

    def __init__(self: Abstract, key: str) -> None:
        self._data: Dict[str, Any] = {}
        self._key = key

    def __getattr__(self: Abstract, key: str) -> Any:
        return self._data

    def __setattr__(self: Abstract, key: str, value: Any) -> None:
        self._data[key] = value
