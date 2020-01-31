from typing import Dict, AnyStr, Awaitable, Optional
from modulo.events import trigger
from .context import Context

class Handler():
    def __init__(self: Handler) -> None:
        self.message_type = self.get_message_type()
        self.context = self.get_context_class()
        self.send: Optional[Awaitable] = None
        self.receive: Optional[Awaitable] = None
        self.keep_running: bool = True

    def get_message_type(self: Handler) -> str:
        return 'NoneType'

    def get_context_class(self: Handler) -> Context:
        return Context()

    async def load_context(self: Handler, params: Dict[str, AnyStr) -> None:
        await self.context.load(params)

    async def load_scope(self: Handler, scope: Dict[str, AnyStr], receive: Awaitable, send: Awaitable) -> None:
        del scope['type']
        self.send = send
        self.receive = receive
        await self.load_context(scope)
    
    async def on_event(self: Handler, event: Dict) -> None:
        pass

    async def run(self: Handler) -> None:
        while self.keep_running:
            event = await self.receive()
            await self.on_event(event)
