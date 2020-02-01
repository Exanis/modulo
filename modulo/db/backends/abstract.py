from typing import List, Tuple, Any, TYPE_CHECKING, Union
from asyncio import Queue


if TYPE_CHECKING:
    from modulo.db.table import Request


class Abstract():
    async def transaction(self: Abstract) -> None:
        raise NotImplementedError()

    async def commit(self: Abstract) -> None:
        raise NotImplementedError()

    async def rollback(self: Abstract) -> None:
        raise NotImplementedError()

    async def execute_query(self: Abstract, sql: str, params: Optional[Union[Tuple[Any], Dict[str, Any]]] = None) -> None:
        raise NotImplementedError()

    async def fetch_one(self: Abstract) -> Tuple[Any]:
        raise NotImplementedError()

    async def fetch_some(self: Abstract, cnt: int) -> List[Tuple[Any]]:
        raise NotImplementedError()

    async def fetch_all(self: Abstract) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    async def count(self: Abstract) -> int:
        raise NotImplementedError()

    async def open(self: Abstract, *args, **kwargs) -> None:
        raise NotImplementedError()

    async def close(self: Abstract) -> None:
        raise NotImplementedError()

    @staticmethod
    def to_sql(request: Request) -> str:
        raise NotImplementedError()

    @staticmethod
    def to_partial_where(key: str, placeholder: str, is_list: bool = False, is_subquery: bool = False, is_none: bool = False) -> str:
        raise NotImplementedError()
    
    @staticmethod
    def where_and(first: str, second: str) -> str:
        raise NotImplementedError()
    
    @staticmethod
    def where_or(first: str, second: str) -> str:
        raise NotImplementedError()