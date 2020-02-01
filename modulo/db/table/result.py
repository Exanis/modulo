from typing import Optional, Tuple, Any, List
from .table import Table


class Result():
    def __init__(self: Result, table: Table, data: Tuple[Any], columns: List[str]) -> None:
        self._table = table
        self._data = {columns[i]: data[i] for i in range(len(columns))}

    def __getattr__(self: Result, key: str) -> Any:
        return self._data[key]
    
    def __setattr__(self: Result, key: str, value: Any) -> None:
        self._data[key] = value
    
    async def save(self: Result) -> None:
        from .request import Request

        if self._table.primary not in self._data:
            raise KeyError(f'Primary key column in {self._table} ({self._table.primary}) was not retrieved when creating this result object, thus it cannot be updated')
        request = Request(self._table, 'UPDATE', self._data)
        request.where({
            self._table.primary: self._data[self._table.primary]
        })
        await request.execute()
    
    async def delete(self: Result) -> None:
        from .request import Request

        if self._table.primary not in self._data:
            raise KeyError(f'Primary key column in {self._table} ({self._table.primary}) was not retrieved when creating this result object, thus it cannot be deleted')
        request = Request(self._table, 'DELETE')
        request.where({
            self._table.primary: self._data[self._table.primary]
        })
        await request.execute()
