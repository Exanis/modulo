from typing import Optional, Union, Dict, Tuple, Any, TYPE_CHECKING
import aiopg
from .abstract import Abstract


if TYPE_CHECKING:
    from modulo.db.table import Request


class Postgres(Abstract):
    def __init__(self: Postgres) -> None:
        self._connection: aiopg.Connection = None
        self._cursor: aiopg.Cursor = None
        self._started = False
        self._done = False
    
    async def open(self: Abstract, dsn: str) -> None:
        self._connection = await aiopg.connect(dsn)
        self._cursor = await self._connection.cursor()

    async def transaction(self: Postgres) -> None:
        await self._cursor.execute('BEGIN;')
        self._started = True
        self._done = False
    
    async def commit(self: Postgres) -> None:
        await self._cursor.execute('COMMIT;')
        self._started = False
        self._done = True
    
    async def rollback(self: Postgres) -> None:
        await self._cursor.execute('ROLLBACK;')
        self._started = False
        self._done = False
    
    async def execute_query(self: Postgres, sql: str, params: Optional[Union[Tuple[Any], Dict[str, Any]]] = None) -> None:
        if not self._started:
            await self.transaction()
        await self._cursor.execute(sql, parameters=params)
    
    async def _check_connection_done(self: Postgres) -> None:
        if not self._done:
            if not self._started:
                raise SyntaxError("Cannot get data / length without request")
            else:
                await self.commit()
    
    async def fetch_all(self: Postgres) -> List[Tuple[Any]]:
        self._check_connection_done()
        return await self._cursor.fetchall()

    async def fetch_one(self: Postgres) -> Tuple[Any]:
        self._check_connection_done()
        return await self._cursor.fetchone()
    
    async def fetch_some(self: Postgres, cnt: int) -> List[Tuple[Any]]:
        self._check_connection_done()
        return await self._cursor.fetchmany(cnt)
    
    async def count(self: Postgres) -> int:
        self._check_connection_done()
        return self._cursor.rowcount
    
    async def close(self: Postgres) -> None:
        if self._started and not self._done:
            await self.rollback()
        self._cursor.close()
        self._connection.close()

    def to_sql(self: Postgres, action: str, request: Request) -> str:
        if action == 'SELECT':
            columns = [f'{column} AS {name}' for name, column in request._columns] if not request._count_only else ['COUNT(id) AS ']
            joins = [f'''{j["type"]} JOIN {j["target"]} AS {id(j["target"]} ON {" AND ".join([f"{id(j['target'])}.{key} = {val}" for key, val in j["on"]])}''' for j in ]
            order_by = 