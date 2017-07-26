# -*- coding: utf-8 -*-

import discord
import json
from datetime import timezone
from collections import defaultdict
import logging
import modules
from event import Event


class Server(object):
    def __init__(self):
        logging.basicConfig(level=logging.WARNING)
        with open("config.json") as file:
            self.config = json.load(file)
        self.client = discord.Client()  # type: discord.Client
        self.client.event(self.on_ready)
        self.client.event(self.on_message_delete)
        self.client.event(self.on_message)
        self.modules = {}  # type: dict
        self.events = defaultdict(list)  # type: defaultdict
        for module in self.config['modules']:
            if self.config['modules'][module]['enabled']:
                self.modules[module] = getattr(modules, module)(self, self.config['modules'][module])

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

        @todo Change it to use pooled callbacks
        @param message: Message object given back from the discord's api
        """
        if self.config['private'] and message.channel.is_private or len(self.config['servers']) == 0 or message.server.id in self.config['servers']:
            print(self.format_message(message))

    async def on_message(self, message: discord.Message):
        """
        http://discordpy.readthedocs.io/en/latest/api.html#discord.on_message

        @param message:
        """
        for func in self.events[Event.ON_MESSAGE]:
            await func(message)

    def format_message(self, message: discord.Message):
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
                output.append(attachment['url'])
        return "[{}] {}: {}".format(
            message.timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None),
            message.author.name,
            ' '.join(output)
        )

    def run(self):
        """
        Main method that starts the whole server
        """
        self.client.run(self.config['token'], bot=self.config['bot'])
