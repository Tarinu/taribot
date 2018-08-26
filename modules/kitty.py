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
        self.config = config  # type: dict
        Module.__init__(self, server)
        try:
            LocalImage.__init__(self, config.get('location', ''))
        except KeyError:
            raise ConfigException("Kitty module config is missing 'location' config")
        self.gfycat = None
        config_keyword = self.config.get('keyword', '')  # type: str
        if not isinstance(config_keyword, str):
            raise ConfigException("Kitty module keyword has to be string")
        if not config_keyword:
            raise ConfigException("Kitty module keyword can't be empty")
        self.keyword = self.server.prefix + config_keyword

        gfycat_config = config.get('gfycat', {})
        if not isinstance(gfycat_config, dict):
            raise ConfigException("Kitty module's gfycat config has to be dict/object")

        if gfycat_config.get('enabled', False):
            gfycat_keyword = gfycat_config.get('keyword', '')
            if not isinstance(gfycat_keyword, str):
                raise ConfigException("Kitty module keyword has to be string")
            if not gfycat_keyword:
                raise ConfigException("Kitty module keyword can't be empty")
            self.gfycat = Gfycat(gfycat_config)
            self.gfycat_keyword = self.server.prefix + gfycat_keyword

        self.add_handler(Event.ON_READY, self.on_ready)
        self.add_handler(Event.ON_MESSAGE, self.on_message)

    async def on_ready(self):
        """
        Discord's on_ready event.
        """
        commands = ["{} <int>".format(self.keyword)]
        if self.gfycat is not None:
            commands.append(self.gfycat_keyword)
        await self.server.client.change_presence(activity=discord.Game(name=", ".join(commands)))
        print('Kitty module loaded')

    async def on_message(self, message: discord.Message):
        """
        This gets triggered on discord's on_message event. Sends an image to the channel where "<prefix>cat" is written
        Possible to also send multiple images with "<prefix>cat <int>"

        @param message
        """
        content = message.clean_content.strip()  # type: str
        split = content.split()  # type: [str]
        if len(split) > 0:
            keyword = split[0].lower()
            if keyword == self.keyword:
                count = 1
                if len(split) >= 2:
                    count = split[1]
                try:
                    await self.send_cat(message.channel, self.validate_send_cat_count(count))
                except ValueError as e:
                    await message.channel.send(e)
            elif self.gfycat is not None and keyword == self.gfycat_keyword:
                await self.send_catvid(message.channel)

    async def send_cat(self, messageable: discord.abc.Messageable, count: int = 1):
        """
        Sends a random image to user/channel.
        If the count comes from user, you should run it through @meth:`validate_send_cat_count`
            to make sure the count is valid

        @param messageable
        @param count: number of pictures to send
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
