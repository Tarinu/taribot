# -*- coding: utf-8 -*-

import discord
import json
import modules
import logging
import sys
from database import Database
from datetime import timezone
from collections import defaultdict
from event import Event

logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self):
        with open("config.json") as file:
            self.config = json.load(file)
        self.client = discord.Client()  # type: discord.Client
        self.client.event(self.on_ready)
        self.client.event(self.on_message_delete)
        self.client.event(self.on_message)
        self.client.event(self.on_error)
        # if self.config.get('database', {}).get('enabled', False):
        #    self.db = Database(self.config.get('database'))
        self.modules = {}  # type: dict
        self.events = defaultdict(list)  # type: defaultdict
        for module in self.config.get('modules', []):
            if self.config.get('modules', {}).get(module, {}).get('enabled', False):
                self.modules[module] = getattr(modules, module)(self, self.config.get('modules').get(module))

    async def on_ready(self):
        """
        http://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
        """
        print('Logged in as')
        print(self.client.user.name)
        print(self.client.user.id)
        print('------')
        for func in self.events[Event.ON_READY]:
            await func()

    async def on_message_delete(self, message: discord.Message):
        """
        This function gets triggered when one of the messages in the message cache gets deleted (defaults to last 5000 messages)
        @see http://discordpy.readthedocs.io/en/latest/api.html#discord.on_message_delete

        @param message: Message object given back from the discord's api
        """
        for func in self.events[Event.ON_MESSAGE_DELETE]:
            await func(message)

    async def on_message(self, message: discord.Message):
        """
        http://discordpy.readthedocs.io/en/latest/api.html#discord.on_message

        @param message:
        """
        if message.author != self.client.user:
            print(self.format_message(message))
        for func in self.events[Event.ON_MESSAGE]:
            await func(message)

    async def on_error(self, event, *args, **kwargs):
        logger.exception("Uncaught Exception in {}".format(event), exc_info=sys.exc_info())

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
