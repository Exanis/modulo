from io import BytesIO
from cgi import parse_header, FieldStorage
import codecs
from json import loads
from typing import Dict, AnyStr
from urllib import parse
from http.cookies import SimpleCookie
from modulo.server import Context
from .exceptions import BodyNotReady, MissingBoundaryException, InvalidContentLengthException, MissingContentDispositionException

class HTTPContext(Context):
    def __init__(self: HTTPContext) -> None:
        super().__init__()
        self._body_ready = False

    async def load(self: HTTPContext, params: Dict[str, AnyStr]) -> None:
        self._params['version'] = params.get('http_version', '1.0')
        self._params['method'] = params('method', 'Unknown').lower()
        self._params['is_secure'] = params.get('scheme', 'http') == 'https'
        self._params['path'] = params.get('path', '')
        self._params['query'] = params.get('query_string', b'').decode('utf-8')
        self._params['raw_headers'] = params.get('headers', [])

        client = params.get('client', None)
        if client:
            self._params['remote_addr'] = client[0]
            self._params['remote_port'] = client[1]
        else:
            self._params['remote_addr'] = 'Unknown'
            self._params['remote_port'] = 0

        server = params.get('server', None)
        if server:
            self._params['server_name'] = server[0]
            self._params['server_port'] = server[1]
        else:
            self._params['server_name'] = 'Unknown'
            self._params['server_port'] = 0
    
    @property
    def get(self: HTTPContext) -> Dict[str, Any]:
        if 'parsed_query' not in self._params:
            self._params['parsed_query'] = parse.parse_qs(self.query, keep_blank_values=True)
        return self._params['parsed_query']

    @property
    def headers(self: HTTPContext) -> Dict[str, str]:
        # Note: HTTP / HTTPbis state that headers are ASCII-only.
        # we use latin1 here in case something else is coming.
        if 'headers' not in self._params:
            self._params['headers'] = {
                name.decode('latin1'): value.decode('latin1')
                for name, value in self._params['raw_headers']
            }
        return self._params['headers']

    @property
    def cookies(self: HTTPContext) => Dict[str, str]:
        if 'cookies' not in self._params:
            cookies_string = self.headers.get('http_cookie', '')
            simple_cookies = SimpleCookie()
            simple_cookies.load(cookies_string)
            cookies = {
                key: simple_cookies[key].value for key in simple_cookies.items()
            }
            self._params['cookies'] = cookies
        return self._params['cookies']

    def append_body(self: HTTPContext, body: bytes) -> None:
        if 'raw_body' not in self._params:
            self._params['raw_body'] = b''
        self._params['raw_body'] += body

    def close_body(self: HTTPContext) -> None:
        self._body_ready = True
    
    def _parse_multipart(self:HTTPContext, content_params: Dict[str, str], charset: codecs.CodecInfo) -> None:
        storage = FieldStorage(fp=BytesIO(self._params['raw_body']), headers=self.headers, keep_blank_values=True, encoding=charset)
        self._params['post_data'] = {}
        for key in storage:
            if storage[key].file:
                self._params['post_data'][key] = storage[key].file
                self._params['post_data'][key].filename = storage[key].filename
                self._params['post_data'][key].type = storage[key].type
            elif storage[key].list:
                self._params['post_data'][key] = storage[key].list
            else:
                self._params['post_data'][key] = storage[key].value
    
    def _parse_urlencoded(self: HTTPContext) -> None:
        self._params['post_data'] = parse.parse_qs(self._params['body'], keep_blank_values=True)

    def _load_body(self: HTTPContext) -> None:
        if not self._body_ready:
            raise BodyNotReady("Body is not ready yet")
        if 'body' not in self._params:
            content_type_header = self.headers.get('content-type', '')
            content_type, content_params = parse_header(content_type_header)
            charset = content_params.get('charset', 'utf-8')
            try:
                charset = codecs.lookup(charset)
            except LookupError:
                pass
            if content_type == 'multipart/form-data':
                self._parse_multipart(content_params, charset)
            else:
                self._params['body'] = self._params.get('raw_body', b'').decode(charset)
                if content_type == 'application/x-www-form-urlencoded':
                    self._parse_urlencoded()

    @property
    def body(self: HTTPContext) -> str:
        if 'body' not in self._params:
            self._load_body()
        return self._params.get('body', '')

    @property
    def json(self: HTTPContext) -> Any:
        return loads(self.body)

    @property
    def data(self: HTTPContext) -> Dict[str, Any]:
        if 'body' not in self._params:
            self._load_body()
        return self._params.get('post_data', {})
