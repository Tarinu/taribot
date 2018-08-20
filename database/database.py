# -*- coding: utf-8 -*-

import aiosqlite
from .query_cursor import QueryCursor
from .connection import Connection


class Database:
    def __init__(self, config: dict):
        self.config = config
        self.connection = Connection(config.get('database', 'taribot.db'))  # type: Connection

    async def create_table(self, table_name: str, columns: dict):
        column_list = []
        for column in columns:
            column_list.append("{} {}".format(column, columns.get(column)))
        await self.execute('CREATE TABLE IF NOT EXISTS {} ( {} )'.format(table_name, ','.join(column_list)))

    async def drop_table(self, table_name: str):
        await self.execute('DROP TABLE {}'.format(table_name))

    async def execute(self, sql: str, *args):
        async with QueryCursor(self.connection, sql, *args) as cursor:  # type: aiosqlite.Cursor
            await self.connection.commit()

    async def test(self):
        await self.create_table('test', {'id': 'integer primary key autoincrement', 'name': 'text not null'})
        await self.drop_table('test')

    async def fetch_one(self, sql: str, *args):
        async with QueryCursor(self.connection, sql, *args) as cursor:  # type: aiosqlite.Cursor
            return await cursor.fetchone()

    async def fetch_all(self, sql: str, *args):
        async with QueryCursor(self.connection, sql, *args) as cursor:  # type: aiosqlite.Cursor
            return await cursor.fetchall()
