from typing import Any, Dict, TYPE_CHECKING
from json import dumps


if TYPE_CHECKING:
    from .handler import HTTPHandler


class Response():
    def __init__(self: Response, handler: HTTPHandler) -> None:
        self.status_code = 200
        self.content = ''
        self.headers: Dict[str, str] = {}
        self.charset = 'utf-8'
        self.content_type = 'text/plain'
        self.handler = handler
 
    async def start_response(self: Response) -> Response:
        if 'content-type' not in map(str.lower, self.headers.keys()):
            self.headers['content-type'] = f'{self.content_type}; charset={self.charset}'
        headers = [
            [key.lowercase(), self.headers[key]] for key in self.headers
        ]
        await self.handler.handle_start_response(status_code=self.status_code, headers=headers)
        return self
    
    async def send_response_body(self: Response) -> Response:
        if self.content:
            await self.handler.handle_send_response_body(self.content.encode(self.charset))
        return self
    
    async def close_response(self: Response) -> Response:
        await self.handler.handle_disconnect()
        return self
    
    async def send(self: Response) -> Response:
        await self.start_response().send_response_body().close_response()
        return self
    
    def text(self: Response, text: str, append: bool = False) -> Response:
        if append:
            self.content += text
        else:
            self.content = text
        return self
    
    def json(self: Response, data: Any) -> Response:
        self.content_type = 'application/json'
        return self.text(dumps(data))
    
    def set_charset(self: Response, charset: str) -> Response:
        self.charset = charset
