# -*- coding: utf-8 -*-

from random import choice
from exceptions import ConfigException
from glob import glob
import discord
import logging

logger = logging.getLogger(__name__)


class LocalImage(object):
    def __init__(self, location: str, client: discord.Client):
        self.location = location.strip()
        if not self.location.endswith('/'):
            self.location += '/'
        self.client = client

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

    async def send_image(self, destination: discord.Channel, count: int = 1):
        """
        Wrapper for sending the picture

        @todo Add multiple images into a single message instead of sending each image as separate message.
            Another possibility is to use something like imgur api to upload images there then send the links to the user

        @param destination: Channel where the image should be sent
        @param count: Number of images to send
        """
        try:
            for i in range(count):
                with open(self.get_random_image(), mode="rb") as file:
                    await self.client.send_file(destination, file)
        except discord.errors.Forbidden as e:
            logger.warning("[{}:{}][{}]: {}".format(str(destination.server), destination.server.id,str(destination), str(e)))
            await self.client.send_message(destination, "No permission to send an attachment")


class WebImage(object):
    """
    @todo make a class that allows getting images from the web using curl or something
    """
    def __init__(self):
        pass
