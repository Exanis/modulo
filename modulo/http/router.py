import re
from typing import Optional, Dict
from uuid import uuid4
from modulo.events import handle, trigger, event_handler
from .context import Context
from .response import Response

class Router():
    _instance = None

    @staticmethod
    def get() -> Router:
        if Router._instance is None:
            Router._instance = Router()
        return Router._instance

    def __init__(self: Router) -> None:
        self._routes: Dict[str, re.Pattern] = {}

    def register(self: Router, route: str, name: str) -> None:
        self._routes[name] = re.compile(route)
    
    @handle('protocol.http.process_request')
    async def handle(self: Router, context: Context, response: Response) -> bool:
        for key in self._routes:
            match = self._routes[key].match(context.path)
            if match is not None:
                params = {
                    'context': context,
                    'response': response,
                    **match.groupdict
                }
                await trigger(key, params)
                return True
        response.status_code = 404
        await response.send()
        return False

def route(route: str, name: Optional[str] = None):
    if name is None:
        uuid = uuid4().hex
        name = 'http.route.{uuid}'
    Router.get().register(route, name)
    def decorate(func):
        event_handler[name] = func
        return func
