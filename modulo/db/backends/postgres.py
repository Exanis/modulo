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

    @staticmethod
    def to_sql(request: Request) -> str:
        if request._action == 'SELECT':
            columns = [f'{column} AS {name}' for name, column in request._columns]
            joins = [f'{j["type"]} JOIN {j["target"]} AS {id(j["target"])} ON {" AND ".join([str(id(j["target"])) + f".{key} = {val}" for key, val in j["on"].items()])}' for j in request._join]
            orders = [f'{order[1:] if order[0] in ["+", "-"] else order} {"DESC" if order[0] == "-" else "ASC"}' for order in request._order_by]
            sql = f"SELECT {', '.join(columns)} FROM {request._table} AS {id(request._table)} {' '.join(joins)}"
            where = str(request._where)
            if where:
                sql = f'{sql} WHERE {where}'
            if request._group_by:
                sql = f'{sql} GROUP BY {", ".join(request._group_by)}'
            if orders:
                sql = f'{sql} ORDER BY {", ".join(orders)}'
            if request._limit >= 0:
                sql = f'{sql} LIMIT {request._limit}'
            if request._offset > 0:
                sql = f'{sql} OFFSET {request._offset}'
            return sql
        elif request._action == 'INSERT':
            columns = [request._columns[key] for key in request._columns]
            params = request._params
            placeholders = [
                f'%({id(request)}{col})s' if not isinstance(params[col], request)
                else params[col].sql
                for col in request._columns
            ]
            sql = f"INSERT INTO {request._table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            return sql
        elif request._action == 'UPDATE':
            params = request._params
            updates = [
                f"{col} = %({id(request)}{col})s" if not isinstance(params[col], Request)
                else params[col].sql
                for col in request._columns
            ]
            sql = f'UPDATE {request._table} AS {id(request._table)} SET {", ".join(updates)}'
            where = str(request._where)
            if where:
                sql = f'{sql} WHERE {where}'
            return sql
        elif request._action == 'DELETE':
            sql = f'DELETE FROM {request._table} AS {id(request._table}'
            where = str(request._where)
            if where:
                sql = f'{sql} WHERE {where}'
            return sql
        else:
            raise TypeError(f"Unsupported action for request: {request._action}")

    @staticmethod
    def to_partial_where(key: str, placeholder: str, is_list: bool = False, is_subquery: bool = False, is_none: bool = False) -> str:
        if is_subquery:
            return f'{key} IN ({placeholder})'
        elif is_list:
            return f'{key} IN (%({placeholder})s)'
        elif is_none:
            return f'{key} IS NULL'
        else:
            return f'{key} = %({placeholder})s'

    @staticmethod
    def where_and(first: str, second: str) -> str:
        return f'({first}) AND ({second})'
    
    @staticmethod
    def where_or(first: str, second: str) -> str:
        return f'({first} OR ({second})'
