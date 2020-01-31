from typing import Dict, List


class Handler():
    _instance = None

    @staticmethod
    def get() -> Handler:
        if Handler._instance is None:
            Handler._instance = Handler()
        return Handler._instance
    
    def __init__(self: Handler) -> None:
        self._handlers: Dict[str, List[callable]] = {}
    
    def __setitem__(self: Handler, key: str, value: callable):
        if key not in self._handlers:
            self._handlers[key] = []
        self._handlers[key].append(value)

    async def trigger(self: Handler, key: str, param: object) -> None:
        if key in self._handlers:
            for handle in self._handlers[key]:
                if not handle(**param):
                    break

async def trigger(event: str, param: object) -> list:
    await Handler.get().trigger(event, param)
