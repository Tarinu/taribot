# -*- coding: utf-8 -*-

import asyncio
import discord
import taribot.modules as modules
import logging
import sys
from typing import Dict, List
from datetime import timezone
from collections import defaultdict

from taribot.config import Config, ConfigException
from taribot.event import Event
from taribot.database import Database
from taribot.module import Module
from taribot.modules.abc import Command

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, config: Config):
        self.config = config
        self.commands = {}  # type: Dict[str, Command]

        if config.database.get('enabled', False):
            self.db = Database(config.database.get('database'))

        self._events = defaultdict(list)  # type: defaultdict
        self._modules = []  # type: List[Module]

        for module in self.config.modules:
            if not isinstance(module, dict):
                raise ConfigException("module has to be dict")
            if module.get('enabled', False):
                self._modules.append(getattr(modules, module.get("class"))(self, module))

        self.command_statuses = []  # type: List[str]
        for command_name in self.commands:
            command = self.commands.get(command_name)
            if command.status() is not None:
                self.command_statuses.append(command.status().format(name=self.prefix + command_name))

        self._client = discord.Client()  # type: discord.Client
        self._client.event(self.on_ready)
        self._client.event(self.on_message_delete)
        self._client.event(self.on_message)
        self._client.event(self.on_error)

    @property
    def client(self) -> discord.Client:
        return self._client

    @property
    def prefix(self) -> str:
        return self.config.prefix

    async def on_ready(self):
        """
        http://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
        """
        print('Logged in as')
        print(self.client.user.name)
        print(self.client.user.id)
        print('------')
        for func in self._events[Event.ON_READY]:
            await func()
        await self.client.change_presence(activity=discord.Game(name=", ".join(self.command_statuses)))

    async def on_message_delete(self, message: discord.Message):
        """
        This function gets triggered when one of the messages in the message cache gets deleted (defaults to last 5000 messages)
        @see http://discordpy.readthedocs.io/en/latest/api.html#discord.on_message_delete

        @param message: Message object given back from the discord's api
        """
        for func in self._events[Event.ON_MESSAGE_DELETE]:
            await func(message)

    async def on_message(self, message: discord.Message):
        """
        http://discordpy.readthedocs.io/en/latest/api.html#discord.on_message

        @param message:
        """
        if message.author != self.client.user:
            if self.config.print_messages:
                print(self.format_message(message))
            content = message.clean_content.strip()  # type: str
            split = content.split()  # type: [str]
            if len(split) > 0:
                keyword = split[0].lower()
                if keyword.startswith(self.prefix):
                    keyword = keyword[len(self.prefix):]
                    if keyword in self.commands:
                        command = self.commands.get(keyword)  # type: Command
                        await command.run(message, *split[1:])

        for func in self._events[Event.ON_MESSAGE]:
            await func(message)

    async def on_error(self, event, *args, **kwargs):
        logger.exception("Uncaught Exception in {}".format(event), exc_info=sys.exc_info())

    def add_event(self, event: Event, func: callable):
        """
        @raise discord.ClientException: If func is not async function or event not supported
        @param event: Event enum value
        @param func: Async function
        """
        if not asyncio.iscoroutinefunction(func):
            raise discord.ClientException("event registered must be a coroutine/async function")
        if not Event.has_value(event):
            raise discord.ClientException("Given event not supported")
        self._events[event].append(func)

    def add_command(self, command: Command):
        """
        Registers a new command users can call
        @param command:
        @raise TypeError: If command isn't modules.abc.Command subclass
        @raise ValueError: If command with the same name already is registered
        """
        if not isinstance(command, Command):
            raise TypeError("command has to inherit the modules.abc.Command class")
        name = command.name
        if name in self.commands:
            raise ValueError("Command {} already registered".format(command))
        self.commands[name] = command

    @staticmethod
    def format_message(message: discord.Message):
        """
        Formats the message to readable format so it's possible to log them in console

        @param message: Discord Message object
        @return: The formatted message
        @rtype str
        """
        output = []
        if message.clean_content.strip():
            output.append(message.clean_content.strip())
        if message.attachments:
            for attachment in message.attachments:
                output.append(attachment.url)
        return "[{}][{}][{}] {}: {}".format(
            message.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None),
            str(message.guild) if message.guild is not None else '-',
            str(message.channel),
            message.author.name,
            ' '.join(output)
        )

    def run(self):
        """
        Main method that starts the whole server
        """
        self.client.run(self.config.token)
