# -*- coding: utf-8 -*-

import asyncio
import sqlite3
import aiosqlite


class Connection(aiosqlite.Connection):
    def __init__(self, database: str, **kwargs):
        def connector() -> sqlite3.Connection:
            return sqlite3.connect(database, **kwargs)
        super().__init__(connector, asyncio.get_event_loop())

    async def __aenter__(self):
        if not self._started.is_set():
            self.start()
        else:
            self._running = True
            self.run()
        await self._connect()
        return self
