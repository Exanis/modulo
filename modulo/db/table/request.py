from typing import List, Dict, Union, Optional, TYPE_CHECKING
from .result import Result


if TYPE_CHECKING:
    from .table import Table


class Request():
    def __init__(self: Request, table: Table) -> None:
        self._count_only = False
        self._columns = {column: column for column in table.columns}
        self._table: Table = table
        self._join: List[Dict[str, str]] = []
        self._limit = -1
        self._offset = 0
        self._order_by: Optional[List[str]] = None
        self._group_by: List[str] = []
        self._where: Dict[str, Union[Request, Result, str, int, float, List[Union[str, int, float], None]]] = {}
    
    def columns(self: Request, columns: Union[str, List[str], Dict[str, str]]) -> Request:
        if isinstance(columns, str):
            columns = {columns: columns}
        elif isinstance(columns, list):
            columns = [column: column for column in columns]
        self._columns = columns
        return self

    def where(self: Request, filters: Dict[str, Union[Request, Result, str, int, float, List[Union[str, int, float], None]]]) -> Request:
        self._where = {
            **self._where,
            **args
        }
        return self

    def group_by(self: Request, target: Union[str, List[str]]) -> Request:
        if not isinstance(target, list):
            target = [target]
        self._group_by = target
        return self
    
    def limit(self: Request, cnt: int) -> Request:
        self._limit = cnt
        return self

    def offset(self: Request, cnt: int) -> Request:
        self._offset = cnt
    
    def order_by(self: Request, by: Union[str, List[str]]) -> Request:
        if not isinstance(by, list):
            by = [by]
        self._order_by = by
        return self
    
    def join(self: Request, target: Table, join_type: str = 'LEFT', **args, **kwargs) -> Request:
        self._join.append({
            "target": target,
            "type": join_type,
            "on": args
        })
        return self
    
    async def select(self: Request, count_only: bool = False) -> Result:
        backend = await self._table.database('read')
        