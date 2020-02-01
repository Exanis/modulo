from typing import Dict, List, Union, Callable, TYPE_CHECKING, Any
from modulo.db.backends import Abstract


if TYPE_CHECKING:
    from .request import Request


class Where():
    def __init__(self: Where, backend: Abstract) -> None:
        self._sql = ''
        self._backend: Abstract = backend
        self._params: Dict[str, Union[str, int, float]] = {}

    def _partial(self: Where, elements: Dict[str, Any]], join: Callable[str, str]) -> None:
        from .request import Request

        for key in args:
            if isinstance(args[key], Request):
                request: Request = args[key]

                if request._action != 'SELECT':
                    raise TypeError('Where object can only accept SELECT request as subquery')

                placeholder = request.sql
                self._params = {
                    **self._params,
                    **request.params
                }
                subquery = True
                is_list = False
            else:
                value = args[key]
                subquery = False
                placeholder = f'{id(self)}{key}'
                if value is None:
                    is_none = True
                    is_list = False
                elif isinstance(value, list):
                    is_list = True
                    is_none = False
                    self._params[placeholder] = value
                else:
                    self._params[placeholder] = value
                    is_none = False
                    is_list = False
            partial = self._backend.to_partial_where(key, placeholder, is_list, subquery, is_none)
            if self._sql:
                self._sql = join(self._sql, partial)
            else:
                self._sql = partial

    def where(self: Where, *args, **kwargs) -> Where:
        self._partial(kwargs, self._backend.where_and)
        return self
    
    def and_where(self: Where, *args, **kwargs) -> Where:
        return self.where(**kwargs)
    
    def or_where(self: Where, *args, **kwargs) -> Where:
        self._partial(kwargs, self._backend.where_or)
        return self

    def append(self: Where, other: Where) -> None:
        if self._sql:
            self._sql = self._backend.where_and(self._sql, other._sql)
        else:
            self._sql = other._sql
        self._params = {
            **self._params,
            other._params
        }
    
    def append_or(self: Where, other: Where) -> None:
        if self._sql:
            self._sql = self._backend.where_or(self._sql, other._sql)
        else:
            self._sql = other._sql
        self._params = {
            **self._params,
            other._params
        }
        
    def __str__(self: Where) -> str:
        return self._sql

    @property
    def params(self: Where) -> Dict[str, Any]:
        return self._params
