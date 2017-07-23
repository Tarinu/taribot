# -*- coding: utf-8 -*-

import discord
from glob import glob
from random import choice
from exceptions import ConfigException
from event import Event
from module import Module


class Kitty(Module):
    def __init__(self, server, config):
        super().__init__(server)
        self.config = config  # type: dict
        self.running = False  # type: bool
        self.server = server  # type: server.Server
        self.client = server.client  # type: discord.Client
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
        if message.channel.is_private and content.startswith('!cat'):
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

    def get_cat_pic(self):
        """
        Picks a random .jpg image from the given location

        @return: Full path of the image
        @rtype str
        """
        self.running = False
        location = self.config['location'].strip()  # type: str
        if location:
            if not location.endswith('/'):
                location += '/'
            return choice(glob(location + '*.jpg'))
        else:
            raise ConfigException('Location value is missing')

    async def send_image(self, destination: discord.Channel, count: int=1):
        """
        Wrapper for sending the picture

        @todo Add multiple images into a single message instead of sending each image as separate message.
            Another possibility is to use something like imgur api to upload images there then send the links to the user

        @param destination: Channel where the image should be sent
        @param count: Number of images to send
        """
        for i in range(count):
            with open(self.get_cat_pic(), mode="rb") as file:
                await self.client.send_file(destination, file)


