from typing import List, Dict, Union, Optional, TYPE_CHECKING, Any
from .result import Result, Line
from .where import Where


if TYPE_CHECKING:
    from .table import Table


class Request():
    def __init__(self: Request, table: Table, action: str, params: Dict[str, Any]) -> None:
        self._count_only = False
        self._columns = {column: column for column in table.columns}
        self._table: Table = table
        self._join: List[Dict[str, str]] = []
        self._action = action
        self._limit = -1
        self._offset = 0
        self._order_by: Optional[List[str]] = None
        self._group_by: List[str] = []
        self._mode = 'read' if action == 'SELECT' else 'write'
        self._backend_type = self._table.get_backend(self._mode)
        self._where: Where = Where(self._backend_type)
        self._having: Where = Where(self._backend_type)
        self._params = params
    
    def columns(self: Request, columns: Union[str, List[str], Dict[str, str]]) -> Request:
        if isinstance(columns, str):
            columns = {columns: columns}
        elif isinstance(columns, list):
            columns = [column: column for column in columns]
        self._columns = columns
        return self

    def where(self: Request, params: Union[Where, Dict[str, Any]]) -> Request:
        if isinstance(params, dict):
            self._where.and_where(**params)
        else:
            self._where.append(params)
        return self

    def or_where(self: Request, params: Union[Where, Dict[str, Any]]) -> Request:
        if isinstance(params, dict):
            self._where.or_where(**params)
        else:
            self._where.append_or(params)
        return self

    def having(self: Request, *args, **kwargs) -> Request:
        if args:
            if not isinstance(args[0], Where):
                raise TypeError(f"Positional parameter to where must be a Where instance, not {type(args[0])}")
            self._having.append(args[0])
        elif kwargs:
            self._having.and_where(**kwargs)
        return self

    def or_having(self: Request, *args, **kwargs) -> Request:
        if args:
            if not isinstance(args[0], Where):
                raise TypeError(f"Positional parameter to where must be a Where instance, not {type(args[0])}")
            self._having.append_or(args[0])
        elif kwargs:
            self._having.or_where(**kwargs)
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
    
    def join(self: Request, target: Table, join_type: str = 'LEFT', *args, **kwargs) -> Request:
        self._join.append({
            "target": target,
            "type": join_type,
            "on": kwargs
        })
        return self
    
    @property
    def sql(self: Request) -> str:
        return self._backend_type.to_sql(self)
    
    @property
    def params(self: Request) -> Dict[str, Any]:
        base_params = {
            **self._where.params,
            **self._having.params
        }
        for param in self._params:
            if isinstance(self._params[param], Request):
                base_params = {
                    **base_params,
                    **self._params[param].params
                }
            else:
                base_params[f"{id(self)}{key}"] = self._params[param]
        return base_params
    
    async def execute(self: Request) -> None:
        backend = await self._table.database(self._mode)
        await backend.execute_query(self.sql, self.params)
        await backend.commit()
        await self._table.release(self._mode, backend)
    
    async def all(self: Request) -> List[Result]:
        backend = await self._table.database(self._mode)
        await backend.execute_query(self._sql, {
            **self._where.params,
            **self._having.params
        })
        data = await backend.fetch_all()
        result = [Result(self._table, line, self._columns.keys()) for line in data]
        await self._table.release(self._mode, backend)
        return result
    
    async def one(self: Request) -> Result:
        backend = await self._table.database(self._mode)
        await backend.execute_query(self._sql, {
            **self._where.params,
            **self._having.params
        })
        data = await backend.fetch_one()
        result = Result(self._table, line, self._columns.keys())
        await self._table.release(self._mode, backend)
        return result
