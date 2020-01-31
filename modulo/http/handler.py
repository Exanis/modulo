from typing import Dict, AnyStr, Any, Awaitable
from modulo.server import Handler
from modulo.events import handle, trigger
from modulo.server import settings
from .context import HTTPContext
from .response import HTTPResponse
from .exceptions import InvalidRequestError

class HTTPHandler(Handler):
    def __init__(self: HTTPHandler) -> None:
        super().__init__()
        self.response: HTTPResponse = HTTPResponse(self)

    def get_message_type(self: HTTPHandler) -> str:
        return 'http'
    
    def get_context_class(self: HTTPHandler) -> HTTPContext:
        return HTTPContext()
    
    async def _trigger(self: HTTPHandler, event: str) -> None:
        await trigger(event, {
            'context': self.context,
            'response': self.response
        })

    async def on_event(self: HTTPHandler, event: Dict) -> None:
        event_type = event.get('type', '')
        if event_type == 'http.request':
            await self.handle_request(**event)
        elif event_type == 'http.disconnect':
            await self.handle_disconnect()

    async def load_scope(self: Handler, scope: Dict[str, AnyStr], scope: Dict[str, AnyStr], receive: Awaitable, send: Awaitable) -> bool:
        await super().load_scope(scope, receive, send)
        await self._trigger('protocol.http.open_connection')
        return True
    
    async def handle_request(self: Handler, type: str, body: bytes, more_body: bool = False) -> bool:
        try:
            self.context.append_body(body)
            await self._trigger('protocol.http.body_part')
            if not more_body:
                self.context.close_body()
                await self._trigger('protocol.http.body_ready')
                if self.keep_running:
                    await self._trigger('protocol.http.request_ready')
                if self.keep_running:
                    await self._trigger('protocol.http.process_request')
                if self.keep_running:
                    await self._trigger('protocol.http.request_end')
            return True
        except Exception as e:
            content = str(e) if settings.DEBUG else ''
            await self.send({
                'type': 'http.response.start',
                'status': 500,
                'headers': []
            })
            await self.send({
                'type': 'http.response.body',
                'body': content.encode('ascii'),
                'more_body': False
            })
            return False

    async def handle_start_response(self: Handler, status_code: int, headers: Any) -> bool:
        await self.send({
            'type': 'http.response.start',
            'status': status_code,
            'headers': headers
        })
        return True
    
    async def handle_send_response_body(self: Handler, content: bytes) -> bool:
        await self.send({
            'type': 'http.response.body',
            'body': content,
            'more_body': True
        })
        return True
    
    async def handle_close_response(self: Handler) -> bool:
        await self.send({
            'type': 'http.response.body',
            'body': b'',
            'more_body': False
        })
        self.keep_running = False
        return True
    
    async def handle_disconnect(self: Handler) -> bool:
        await self._trigger('protocol.http.disconnect')
        self.keep_running = False
        return True
