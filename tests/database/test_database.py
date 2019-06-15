#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from unittest import TestCase
from database import Database
import os


class TestDatabase(TestCase):
    database = None
    test_table_name = 'test'
    test_database_name = 'test.db'

    @classmethod
    def setUpClass(cls):
        cls.database = Database({'database': cls.test_database_name})

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_database_name)

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def test_table_methods(self):
        async def test_create_table():
            await self.database.create_table(self.test_table_name, {'id': 'integer primary key autoincrement'})
            created = await self.database.fetch_one("SELECT * FROM sqlite_master WHERE type='table' AND name=?", self.test_table_name)
            self.assertIsNotNone(created)

        async def test_drop_table():
            await self.database.drop_table(self.test_table_name)
            deleted = await self.database.fetch_one("SELECT * FROM sqlite_master WHERE type='table' AND name=?", self.test_table_name)
            self.assertIsNone(deleted)

        self.loop.run_until_complete(test_create_table())
        self.loop.run_until_complete(test_drop_table())
