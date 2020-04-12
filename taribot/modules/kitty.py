# -*- coding: utf-8 -*-

import discord
import logging
from taribot.modules.abc import SchedulableCommand
from taribot.module import Module
from typing import Union
from taribot.event import Event
from taribot.modules import LocalImage
from taribot.config import ConfigException
from taribot.apis import Gfycat

logger = logging.getLogger(__name__)


class Kitty(Module, LocalImage):
    def __init__(self, server, config: dict):
        self.config = config
        Module.__init__(self, server)
        image_location = config.get('location')
        if not image_location:
            raise ConfigException("Kitty module config is missing location config")
        LocalImage.__init__(self, image_location)

        self.gfycat = None
        keyword = config.get('keyword', 'cat')  # type: str
        if not isinstance(keyword, str):
            raise ConfigException("Kitty module keyword has to be string")
        keyword = keyword.strip()
        if not keyword:
            raise ConfigException("Kitty module keyword can't be empty")
        max_images = config.get('max_images', 5)
        if not isinstance(max_images, int):
            raise ConfigException("Kitty module max_images has to be integer")
        if max_images < 1:
            raise ConfigException("Kitty module max_images has to be at least 1")

        self.add_command(CatCommand(self, keyword, max_images))

        gfycat_config = config.get('gfycat', {})
        if not isinstance(gfycat_config, dict):
            raise ConfigException("Kitty module's gfycat config has to be dict/object")

        if gfycat_config.get('enabled', False):
            gfycat_keyword = gfycat_config.get('keyword', 'catvid')
            if not isinstance(gfycat_keyword, str):
                raise ConfigException("Kitty module keyword has to be string")
            if not gfycat_keyword:
                raise ConfigException("Kitty module keyword can't be empty")
            self.add_command(CatvidCommand(self, gfycat_keyword, Gfycat(gfycat_config)))

        self.add_handler(Event.ON_READY, self.on_ready)

    async def on_ready(self):
        """
        Discord's on_ready event.
        """
        print('Kitty module loaded')


class CatCommand(SchedulableCommand):
    def __init__(self, module: Kitty, name: str, max_images: int):
        super(CatCommand, self).__init__(module, name)
        self.max_images = max_images

    def validate(self, count: int) -> bool:
        try:
            self.validate_count(count)
            return True
        except ValueError:
            return False

    def help(self) -> str:
        return "Posts x number of cat images in the chat (max number of images {}). Defaults to 1 if no number given".format(self.max_images)

    def status(self):
        return "{name} <int>"

    async def run(self, message: discord.Message, count: int = 1, *args, **kwargs):
        await self.send(message.channel, count)

    async def send(self, messageable: discord.abc.Messageable, count: int = 1, *args, **kwargs):
        """
        Sends a random image to user/channel.
        If the count comes from user, you should run it through @meth:`validate_send_cat_count`
            to make sure the count is valid

        @param messageable
        @param count: number of pictures to send
        """
        try:
            await self.module.send_image(messageable, self.validate_count(count))
        except ValueError as e:
            await messageable.send(e)

    def validate_count(self, count: Union[int, str]) -> int:
        """
        Validated that count is a number and it's between 1 and maximum number of pics allowed in config file

        @param count:
        @return: count as integer
        @raise ValueError: count is not a valid number
        """
        try:
            count = int(count)
        except ValueError:
            raise ValueError('Picture count has to be an integer')
        if count > self.max_images:
            raise ValueError('Picture count can be maximum {}'.format(self.max_images))
        elif count < 1:
            raise ValueError('Picture count has to be at least 1')
        return count


class CatvidCommand(SchedulableCommand):
    def __init__(self, module: Kitty, name: str, gfycat: Gfycat):
        super(CatvidCommand, self).__init__(module, name)
        self.gfycat = gfycat

    def status(self) -> str:
        return "{name}"

    async def run(self, message: discord.Message, *args, **kwargs):
        await self.send(message.channel)

    async def send(self, messageable: discord.abc.Messageable, *args, **kwargs):
        try:
            message = await self.gfycat.get_random_gfycat()
        except Exception as e:
            logger.exception("Unable to get video from gfycat", exc_info=e)
            message = e
        await messageable.send(message)
