# -*- coding: utf-8 -*-

import discord
import json
from datetime import timezone
import logging
import modules


class Server(object):
    def __init__(self):
        logging.basicConfig(level=logging.WARNING)
        with open("config.json") as file:
            self.config = json.load(file)
        self.client = discord.Client()
        self.client.event(self.on_ready)
        self.client.event(self.on_message_delete)
        self.client.event(self.on_message)
        self.modules = {}
        # todo abstract module loading
        for module in self.config['modules']:
            if self.config['modules'][module]['enabled']:
                self.modules[module] = getattr(modules, module.capitalize())(self.client, self.config['modules'][module])

    async def on_ready(self):
        print('Logged in as')
        print(self.client.user.name)
        print(self.client.user.id)
        print('------')
        print('Modules Loaded:')
        for module in self.modules:
            print(module)

    async def on_message_delete(self, message: discord.Message):
        if self.config['private'] and message.channel.is_private or not self.config['servers'] or message.server.id in self.config['servers']:
            print(self.format_message(message))

    async def on_message(self, message: discord.Message):
        if 'kitty' in self.modules.keys() and message.channel.is_private and message.clean_content.strip().startswith('!cat'):
            await self.modules['kitty'].send_image(message.channel)

    def format_message(self, message: discord.Message):
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
        if self.config['bot']:
            self.client.run(self.config['token'])
        else:
            self.client.run(self.config['username'], self.config['password'])
