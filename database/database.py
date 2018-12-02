# -*- coding: utf-8 -*-

import aiosqlite


class Database:
    def __init__(self, config: dict):
        self.config = config
        self.database = config.get('database', 'taribot.db')

    async def create_table(self, table_name: str, columns: dict):
        column_list = []
        for column in columns:
            column_list.append("{} {}".format(column, columns.get(column)))
        await self.execute('CREATE TABLE IF NOT EXISTS {} ( {} )'.format(table_name, ','.join(column_list)))

    async def drop_table(self, table_name: str):
        await self.execute('DROP TABLE {}'.format(table_name))

    async def execute(self, sql: str, *args):
        async with aiosqlite.connect(self.database) as connection:  # type: aiosqlite.Connection
            await connection.execute(sql, args)
            await connection.commit()

    async def fetch_one(self, sql: str, *args):
        async with aiosqlite.connect(self.database) as connection:  # type: aiosqlite.Connection
            cursor = await connection.execute(sql, args)
            return await cursor.fetchone()

    async def fetch_all(self, sql: str, *args):
        async with aiosqlite.connect(self.database) as connection:  # type: aiosqlite.Connection
            cursor = await connection.execute(sql, args)
            return await cursor.fetchall()
