from typing import Dict, Union
from modulo.conf import settings
from modulo.db.pool import Pool
from modulo.db.backends import Abstract


class Table():
    _columns: Dict = {}
    _databases: Dict[str, str] = {}

    def __init__(self: Table) -> None:
        if 'read' not in self._databases:
            self._databases['read'] = 'default'
        if 'write' not in self._databases:
            self._databases['write'] = 'default'
    
    @property
    def columns(self: Table) -> List[str]:
        return self._columns.keys()
    
    async def database(self: Table, mode: str) -> Abstract:
        if mode not in self._databases:
            raise KeyError(f"Mode not supported: {mode}")
        pool: Pool = settings.DATABASES[self._databases[mode]]
        return await pool.get()