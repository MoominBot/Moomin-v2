import logging
import typing as t
from contextlib import asynccontextmanager

import aiofiles
import asyncpg

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _acquire(pool: asyncpg.Pool) -> asyncpg.Connection:
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                yield conn
    finally:
        pass


class DatabaseManager:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self._pool = None

    async def establish_connection(self) -> None:
        self._pool = await asyncpg.create_pool(self.dsn)
        logger.info("Connected to the database!")

    async def close_connection(self) -> None:
        assert self._pool is not None
        await self._pool.close()
        logger.info("Disconnected from the database!")

    async def migrate(self) -> None:
        async with aiofiles.open("./migrations/migration.sql") as f:
            await self.execute((await f.read()))

        logger.info("Database migrated successfully!")

    async def execute(self, command: str, *args: t.Any) -> None:
        async with _acquire(self._pool) as conn:
            await conn.execute(command, *args)

    async def execute_many(self, command: str, args: list[t.Any]) -> None:
        async with _acquire(self._pool) as conn:
            await conn.executemany(command, args)

    async def fetch_val(self, command: str, *args: t.Any, column: int = 0) -> t.Any:
        async with _acquire(self._pool) as conn:
            return await conn.fetchval(command, *args, column=column)

    async def fetch_column(
        self, command: str, *args: t.Any, column: int = 0
    ) -> list[t.Any]:
        async with _acquire(self._pool) as conn:
            return [record[column] for record in await conn.fetch(command, *args)]

    async def fetch_record(self, command: str, *args: t.Any) -> asyncpg.Record:
        async with _acquire(self._pool) as conn:
            return await conn.fetchrow(command, *args)

    async def fetch_all(self, command: str, *args: t.Any) -> list[asyncpg.Record]:
        async with _acquire(self._pool) as conn:
            return await conn.fetch(command, *args)
