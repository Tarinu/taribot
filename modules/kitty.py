# -*- coding: utf-8 -*-

import discord
from event import Event
from module import Module
from modules.image import LocalImage
from exceptions import ConfigException


class Kitty(Module, LocalImage):
    def __init__(self, server, config):
        Module.__init__(self, server)
        try:
            LocalImage.__init__(self, config['location'], server.client)
        except KeyError:
            raise ConfigException("Kitty module is missing 'location' config")
        self.config = config  # type: dict
        self.server = server  # type: server.Server
        self.add_handler(Event.ON_READY, self.on_ready)
        self.add_handler(Event.ON_MESSAGE, self.on_message)

    async def on_ready(self):
        """
        Discord's on_ready event.
        """
        print('Kitty module loaded')

    async def on_message(self, message: discord.Message):
        """
        This gets triggered on discord's on_message event. Sends an image to the channel where "!cat" is written
        Possible to also send multiple images with "!cat <int>"

        @param message:
        """
        content = message.clean_content.strip()  # type: str
        if (message.channel.is_private or not self.config['private_only'] and not message.channel.is_private) and content.lower().startswith(self.config['keyword']):
            split = content.split()  # type: [str]
            if len(split) >= 2:
                if split[1].isnumeric():
                    count = int(split[1])
                    if self.config['max_pics'] >= count >= 1:
                        await self.send_image(message.channel, count)
                    elif count <= 1:
                        await self.client.send_message(message.channel, 'Picture count has to be at least 1')
                    else:
                        await self.client.send_message(message.channel, 'Picture count can be maximum {}'.format(self.config['max_pics']))
                else:
                    await self.client.send_message(message.channel, 'Picture count has to be an integer')
            else:
                await self.send_image(message.channel)
