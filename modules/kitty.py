# -*- coding: utf-8 -*-

import discord
import logging
from typing import Union
from event import Event
from module import Module
from modules.image import LocalImage
from exceptions import ConfigException
from apis import Gfycat

logger = logging.getLogger(__name__)


class Kitty(Module, LocalImage):
    def __init__(self, server, config):
        Module.__init__(self, server)
        try:
            LocalImage.__init__(self, config['location'])
        except KeyError:
            raise ConfigException("Kitty module is missing 'location' config")
        self.gfycat = None
        self.client = server.client
        if config.get('gfycat', {}).get('enabled', False):
            self.gfycat = Gfycat(config.get('gfycat'))
        self.config = config  # type: dict
        self.add_handler(Event.ON_READY, self.on_ready)
        self.add_handler(Event.ON_MESSAGE, self.on_message)

    async def on_ready(self):
        """
        Discord's on_ready event.
        """
        commands = ["{} <int>".format(self.config.get('keyword'))]
        if self.gfycat is not None:
            commands.append(self.gfycat.config.get('keyword'))
        await self.client.change_presence(activity=discord.Game(name=", ".join(commands)))
        print('Kitty module loaded')

    async def on_message(self, message: discord.Message):
        """
        This gets triggered on discord's on_message event. Sends an image to the channel where "!cat" is written
        Possible to also send multiple images with "!cat <int>"

        @param message:
        """
        content = message.clean_content.strip()  # type: str
        split = content.split()  # type: [str]
        if len(split) >= 1 and (isinstance(message.channel, discord.abc.PrivateChannel) or not self.config['private_only'] and not isinstance(message.channel, discord.abc.PrivateChannel)):
            if split[0].lower() == self.config['keyword']:
                count = 1
                if len(split) >= 2:
                    count = split[1]
                try:
                    await self.send_cat(message.channel, self.validate_send_cat_count(count))
                except ValueError as e:
                    await message.channel.send(e)
            elif self.gfycat is not None and split[0].lower() == self.gfycat.config.get('keyword'):
                await self.send_catvid(message.channel)

    async def send_cat(self, messageable: discord.abc.Messageable, count: int = 1):
        """
        Sends a random image to user/channel.
        If the count comes from user, you should run it through @meth:`validate_send_cat_count`
            to make sure the count is valid

        @param messageable:
        @param count:
        """
        await self.send_image(messageable, count)

    def validate_send_cat_count(self, count: Union[int, str]) -> int:
        """
        Validated that count is a number and it's between 1 and maximum number of pics allowed in config file

        @param count:
        @return: count as integer
        @raise ValueError: if count is not a valid number
        """
        try:
            count = int(count)
        except ValueError:
            raise ValueError('Picture count has to be an integer')
        if count > self.config.get('max_pics'):
            raise ValueError('Picture count can be maximum {}'.format(self.config.get('max_pics')))
        elif count < 1:
            raise ValueError('Picture count has to be at least 1')
        return count

    async def send_catvid(self, messageable: discord.abc.Messageable):
        try:
            message = await self.gfycat.get_random_gfycat()
        except Exception as e:
            logger.exception("Unable to get vid from gfycat", exc_info=e)
            message = e
        await messageable.send(message)
