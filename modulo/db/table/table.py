from typing import Dict, Union
from modulo.conf import settings
from modulo.db.pool import Pool
from modulo.db.backends import Abstract
from .request import Request
from .where import Where


class Table():
    _columns: Dict = {}
    _databases: Dict[str, str] = {}
    _name: str = ""
    _primary: str = "id"

    def __init__(self: Table) -> None:
        if 'read' not in self._databases:
            self._databases['read'] = 'default'
        if 'write' not in self._databases:
            self._databases['write'] = 'default'
        if self._primary not in self._columns:
            raise TypeError(f"Primary key {self._primary} is not defined as a column")
    
    @property
    def columns(self: Table) -> List[str]:
        return self._columns.keys()

    @property
    def primary(self: Table) -> str:
        return self._primary
    
    def _get_pool(self: Table, mode: str) -> Pool:
        if mode not in self._databases:
            raise KeyError(f"Mode not supported: {mode}")
        pool: Pool = settings.DATABASES[self._databases[mode]]
        return pool
    
    async def database(self: Table, mode: str) -> Abstract:
        pool = self._get_pool(mode)
        return await pool.get()
    
    async def release(self: Table, mode: str, connection: Abstract):
        await self._get_pool(mode).release(connection)
    
    def __str__(self: Table) -> str:
        return self._name

    def get_backend(self: Table, mode: str) -> Abstract:
        pool = self._get_pool(mode)
        return pool._backend
    
    def __getattr__(self: Table, key: str) -> str:
        return f'{id(self)}.{key}'
    
    def select(self: Table) -> Request:
        return Request(self, 'SELECT')
    
    def update(self: Table) -> Request:
        return Request(self, 'UPDATE')
    
    def delete(self: Table) -> Request:
        return Request(self, 'DELETE')
    
    def where(self: Table, mode: str = None) -> Where:
        if mode is None:
            if self._databases['read'] != self._databases['write']:
                raise TypeError("Cannot create a where object without mode when read and write databases are not the same")
            else:
                mode = 'read'
        return Where(self.get_backend(mode))

    def columns(self: Table, columns: Union[str, List[str], Dict[str, str]]) -> Request:
        return self.select().columns(columns)
