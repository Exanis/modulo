from typing import Dict, Union
from modulo.conf import settings
from modulo.db.pool import Pool
from modulo.db.backends import Abstract


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
