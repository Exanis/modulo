from typing import Dict, Any, List, Awaitable
from time import time
from asyncio import Queue, QueueEmpty
from .backends import Abstract


class Pool():
    def __init__(self: Pool, options: Dict[str, Any]) -> None:
        backend_opts: Dict[str, Any] = options.get('backend', {})
        self._backend_opts: Dict[str, Any] = backend_opts.get('options', {})
        self._backend: type = backend_opts.get('type', Abstract)
        self._lifetime: int = options.get('lifetime', 0)
        self._size: int = options.get('pool_size', 10)
        self._cnt = 0
        self._queue = Queue()
    
    async def get(self: Pool) -> Abstract:
        try:
            item = self._queue.get_nowait()
        except QueueEmpty:
            if self._cnt < self._size:
                item: Abstract = self._backend(**self._backend_opts)
                await item.open()
                item.born = time()
                self._cnt += 1
            else:
                item = await self._queue.get()
        return item
    
    async def release(self: Pool, item: Abstract) -> None:
        if item.born + self._lifetime <= time():
            await item.close()
            self._cnt -= 1
        else:
            self._queue.put_nowait(item)
        return result

    def get_backend(self: Pool) -> type:
        return self._backend
