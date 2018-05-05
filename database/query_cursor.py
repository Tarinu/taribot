# -*- coding: utf-8 -*-

import aiosqlite


class QueryCursor:
    def __init__(self, connection: aiosqlite.Connection, sql: str, *args):
        self.connection = connection
        self.sql = sql
        self.args = args
        self.cursor = None  # type: aiosqlite.Cursor

    async def __aenter__(self):
        await self.connection.__aenter__()
        self.cursor = await self.connection.cursor()
        await self.cursor.execute(self.sql, self.args)
        return self.cursor

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.cursor is not None:
            await self.cursor.close()
            self.cursor = None
        await self.connection.__aexit__(exc_type, exc_val, exc_tb)
