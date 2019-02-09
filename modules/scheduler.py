# -*- coding: utf-8 -*-

import apscheduler.job
import logging
import discord
import sqlite3

from discord import Message
from discord.abc import Messageable

import modules.abc
from event import Event
from module import Module
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Union

logger = logging.getLogger(__name__)


class Scheduler(Module):
    def __init__(self, server, config: dict):
        self.config = config  # type: dict
        Module.__init__(self, server)
        self.jobs = {}
        self.scheduler = AsyncIOScheduler()

        keyword = config.get("keyword", "schedule")
        remove_keyword = config.get("remove_keyword", "unschedule")
        self.add_command(ScheduleCommand(self, keyword))
        self.add_command(UnscheduleCommand(self, remove_keyword))

        self.add_handler(Event.ON_READY, self.on_ready)

    async def run(self, user_id: int, command: str):
        command = command.split(' ')
        command_object = self.server.commands.get(command[0], None)  # type: modules.abc.SchedulableCommand
        if command_object is None:
            logging.error("Command {} not available. Removing schedule job".format(command[0]))
            self.remove_job(user_id)
            return False
        elif not isinstance(command_object, modules.abc.SchedulableCommand):
            logging.warning("Command {} not schedulable. Removing schedule job".format(command[0]))
            self.remove_job(user_id)
            return False
        user = self.server.client.get_user(user_id)  # type: discord.User
        if user is None:
            logger.warning("User with id {} not found. Removing job", user_id)
            self.remove_job(user_id)
            return False
        channel = user.dm_channel  # type: discord.DMChannel
        if channel is None:
            channel = await user.create_dm()
        await command_object.send(channel, *command[1:])

    async def on_ready(self):
        if not self.scheduler.running:
            await self.init_scheduler()

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


class ScheduleCommand(modules.abc.Command):
    def __init__(self, module: Scheduler, name: str):
        super(ScheduleCommand, self).__init__(module, name)

    async def run(self, message: Message, *args, **kwargs):
        if len(args) > 1:
            cmd = args[0].lower()
            command = self.module.server.commands.get(cmd, None)
            if isinstance(command, modules.abc.SchedulableCommand):
                interval = args[-1]
                try:
                    interval = self.validate_interval(interval)
                    try:
                        await self.register_new_schedule(message.author.id, ' '.join(args[:-1]), interval)
                        await message.channel.send(
                            "`{}` scheduled to run every {} minutes".format(' '.join(args[:-1]), interval))
                    except sqlite3.IntegrityError:
                        await message.channel.send("You already have a command scheduled")
                except ValueError:
                    await message.channel.send("Invalid interval {}".format(interval))
            else:
                await message.channel.send("Command \"{}\" is not schedulable".format(cmd))
        else:
            await message.channel.send("Not enough parameters given, should be minimum 2 (command name and interval)")

    def validate(self, command: str = None, *args, **kwargs):
        return isinstance(self.module.server.commands.get(command, None), modules.abc.SchedulableCommand)

    def validate_interval(self, count: Union[int, str]) -> int:
        try:
            count = int(count)
        except ValueError:
            raise ValueError('Interval has to be an integer')
        if count < 1:
            raise ValueError('Interval has to be at least 1')
        return count

    async def register_new_schedule(self, user_id: int, command: str, interval: int):
        await self.module.server.db.execute("INSERT INTO schedule (user_id, command, interval) values (?, ?, ?)", user_id, command, interval)
        self.module.add_job(user_id, command, interval)


class UnscheduleCommand(modules.abc.Command):
    def __init__(self, module: Scheduler, name: str):
        super(UnscheduleCommand, self).__init__(module, name)

    async def run(self, message: Message, *args, **kwargs):
        try:
            await self.remove_schedule(message.author.id)
            await message.channel.send("Schedule removed")
        except Exception as e:
            logger.exception("Removed to unschedule", exc_info=e)
            await message.channel.send("Unable to remove scheduled task")

    async def remove_schedule(self, user_id: int):
        await self.module.server.db.execute("DELETE FROM schedule WHERE user_id = ?", user_id)
        self.module.remove_job(user_id)
