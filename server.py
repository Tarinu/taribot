# -*- coding: utf-8 -*-

import asyncio
import discord
import json
import modules
import logging
import sys
from database import Database
from datetime import timezone
from collections import defaultdict
from event import Event
from exceptions import ConfigException

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self):
        with open("config.json") as file:
            self.config = json.load(file)
        self.prefix = self.config.get('prefix', '')  # type: str
        if not isinstance(self.prefix, str):
            raise ConfigException("Prefix has to be a string")
        if not self.prefix:
            raise ConfigException("Prefix can't be empty")
        if self.config.get('database', {}).get('enabled', False):
            self.db = Database(self.config.get('database'))

        self._events = defaultdict(list)  # type: defaultdict
        self.modules = {}  # type: dict
        config_modules = self.config.get('modules', {})  # type: dict
        if not isinstance(config_modules, dict):
            raise ConfigException("Modules has to be a dict/object")
        for module in config_modules:
            config_module = config_modules.get(module, {})
            if not isinstance(config_module, dict):
                raise ConfigException("{} module has to be dict/object".format(module))
            if config_module.get('enabled', False):
                self.modules[module] = getattr(modules, module)(self, config_modules.get(module))

        self.client = discord.Client()  # type: discord.Client
        self.client.event(self.on_ready)
        self.client.event(self.on_message_delete)
        self.client.event(self.on_message)
        self.client.event(self.on_error)

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
            print(self.format_message(message))
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
        self.client.run(self.config['token'], bot=self.config['bot'])
