# -*- coding: utf-8 -*-

import apscheduler.job
import logging
import discord
import asyncio
import sqlite3
from event import Event
from module import Module
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Union

logger = logging.getLogger(__name__)


class Scheduler(Module):
    def __init__(self, server, config):
        self.config = config  # type: dict
        Module.__init__(self, server)
        self.jobs = {}
        self.scheduler = AsyncIOScheduler()

        self.keyword = self.server.prefix + 'schedule'
        self.remove_keyword = self.server.prefix + 'unschedule'
        self.add_handler(Event.ON_MESSAGE, self.on_message)
        self.add_handler(Event.ON_READY, self.on_ready)

    async def run(self, id: int, command: str):
        user = self.server.client.get_user(id)  # type: discord.User
        command = command.split(' ')
        if user is None:
            logger.warning("User with id {} not found. Removing job", id)
            self.jobs.get(id).remove()
            return False
        channel = user.dm_channel  # type: discord.DMChannel
        if channel is None:
            channel = await user.create_dm()
        func = self.server.commands.get(command[0], None)
        if func is None:
            logging.error("Command {} not available. Removing schedule job".format(command[0]))
        else:
            await func(channel, *command[1:])

    async def on_message(self, message: discord.Message):
        content = message.clean_content.strip()  # type: str
        split = content.split()  # type: [str]
        if len(split) > 2:
            keyword = split[0].lower()
            if keyword == self.keyword:
                command = split[1]
                if command in self.server.commands:
                    interval = split[-1]
                    try:
                        interval = self.validate_interval(interval)
                        try:
                            await self.register_new_schedule(message.author.id, ' '.join(split[1:-1]), interval)
                            await message.channel.send("{} scheduled to run every {} minutes".format(' '.join(split[1:-1]), interval))
                        except sqlite3.IntegrityError as e:
                            await message.channel.send("You already have a command scheduled")
                    except ValueError:
                        await message.channel.send("Invalid interval {}".format(interval))
                else:
                    await message.channel.send("Invalid command {}".format(command))
        elif len(split) == 1:
            if split[0] == self.remove_keyword:
                try:
                    await self.remove_schedule(message.author.id)
                    await message.channel.send("Schedule removed")
                except Exception as e:
                    logger.error(e)
                    await message.channel.send("Unable to remove scheduled task")

    async def on_ready(self):
        if not self.scheduler.running:
            await self.init_scheduler()

    def validate_interval(self, count: Union[int, str]) -> int:
        try:
            count = int(count)
        except ValueError:
            raise ValueError('Interval has to be an integer')
        if count < 1:
            raise ValueError('Interval has to be at least 1')
        return count

    async def init_scheduler(self):
        rows = await self.server.db.fetch_all("SELECT * FROM schedule")
        for row in rows:
            self.add_job(row['user_id'], row['command'], row['interval'])
        self.scheduler.start()

    def add_job(self, user_id: int, command: str, interval: int):
        self.jobs[user_id] = self.scheduler.add_job(self.run, 'interval', (user_id, command), seconds=60 * interval)
        logging.info("Added new job: {} for {} every {} min".format(command, user_id, interval))

    def remove_job(self, user_id: int):
        job = self.jobs.get(user_id, None)  # type: apscheduler.job.Job
        if job is not None:
            job.remove()

    async def register_new_schedule(self, user_id: int, command: str, interval: int):
        await self.server.db.execute("INSERT INTO schedule (user_id, command, interval) values (?, ?, ?)", user_id, command, interval)
        self.add_job(user_id, command, interval)

    async def remove_schedule(self, user_id: int):
        await self.server.db.execute("DELETE FROM schedule WHERE user_id = ?", user_id)
        self.remove_job(user_id)
