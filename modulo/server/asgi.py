from typing import Dict, AnyStr, Awaitable, Optional
from importlib import import_module
from modulo.server import Handler
from modulo.http import HTTPHandler
from modulo.conf import settings, ImproperConfigurationException


class ASGI2Compatibility():
    def __init__(self: ASGI2Compatibility, scope: Dict[str, AnyStr], handler: Handler) -> None:
        self._scope = scope
        self._handler = handler
    
    async def __call__(self: ASGI2Compatibility, receive: Awaitable, send: Awaitable) -> None:
        await self._handler.load_scope(scope, receive, send)
        await self._handler.run()


class ASGIServer():
    def __init__(self: ASGIServer) -> None:
        if not settings.ROUTES:
            raise ImproperConfigurationException('No route have been registered!')
        for route in settings.ROUTES:
            import_module(route)
        self._handlers = {
            'http': HTTPHandler,
            **settings.CUSTOM_HANDLERS
        }
    
    async def __call__(self: ASGIServer, scope: Dict[str, AnyStr], receive: Optional[Awaitable] = None, send: Optional[Awaitable] = None) -> None:
        event_type = scope.get('type', '')
        if event_type not in self._handlers:
            raise ValueError(f'Unsupported scope type {event_type}')
        asgi_version = scope.get('asgi', {}).get('version', '2.0')
        if asgi_version < '3.0':
            return ASGI2Compatibility(scope, self._handlers[event_type])
        await self._handlers[event_type].load_scope(scope, receive, send)
        await self._handlers[event_type].run()
