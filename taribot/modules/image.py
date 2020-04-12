# -*- coding: utf-8 -*-

from random import choice
from taribot.config import ConfigException
from glob import glob
from PIL import Image
from io import BytesIO
import discord
import logging
import os

logger = logging.getLogger(__name__)


class LocalImage(object):
    def __init__(self, location: str, *, max_width: int = 1920, max_height: int = 1920):
        self.location = location.strip()
        if not self.location.endswith('/'):
            self.location += '/'
        self.max_width = max_width
        self.max_height = max_height

    def get_random_image(self):
        """
        Picks a random .jpg image from the given location

        @return: Full path of the image
        @rtype str
        """
        if self.location:
            return choice(glob(self.location + '*.jpg'))
        else:
            raise ConfigException('Location value is missing')

    async def send_image(self, channel: discord.abc.Messageable, count: int = 1):
        """
        Wrapper for sending the picture

        @param channel: Channel where the image should be sent
        @param count: Number of images to send
        """
        try:
            files = []
            bytes_sent = 0
            for i in range(count):
                path = self.get_random_image()
                image = Image.open(path)
                image.thumbnail((self.max_width, self.max_height))
                bytes_io = BytesIO()
                image.save(bytes_io, "JPEG")
                _, filename = os.path.split(path)
                bytes_sent += len(bytes_io.getvalue())
                bytes_io.seek(0)
                files.append(discord.File(bytes_io, filename))
            logger.info("Trying to send {} KB".format(bytes_sent / 1024))
            await channel.send(files=files)
        except discord.errors.Forbidden as e:
            if isinstance(channel, discord.abc.GuildChannel):
                logger.warning("[{}:{}][{}]: {}".format(str(channel.guild), channel.guild.id, str(channel), str(e)))
            elif isinstance(channel, discord.abc.PrivateChannel):
                logger.warning("[{}]: {}".format(str(channel), str(e)))
            try:
                await channel.send("No permission to send an attachment")
            except discord.errors.Forbidden as e:
                if isinstance(channel, discord.abc.GuildChannel):
                    logger.warning("[{}:{}][{}]: {}".format(str(channel.guild), channel.guild.id, str(channel), str(e)))
                elif isinstance(channel, discord.abc.PrivateChannel):
                    logger.warning("[{}]: {}".format(str(channel), str(e)))


class WebImage(object):
    """
    @todo make a class that allows getting images from the web using aiohttp (for example get image from danbooru api from given keyword)
    """
    def __init__(self):
        pass
