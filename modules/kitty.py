# -*- coding: utf-8 -*-

from threading import Timer
from glob import glob
from random import choice
from exceptions import ConfigException


class Kitty(object):
    def __init__(self, client, config):
        self.config = config
        self.running = False
        self.timer = None
        self.client = client
        if self.config['autostart']:
            self.start()
        print('Kitty module loaded')

    def get_cat_pic(self):
        self.running = False
        self.start()
        location = self.config['location'].strip()  # type: String
        if location:
            if not location.endswith('/'):
                location += '/'
            return choice(glob(location + '*.jpg'))
        else:
            raise ConfigException('Location value is missing')

    async def send_image(self, destination):
        with open(self.get_cat_pic(), mode="rb") as file:
            await self.client.send_file(destination, file)

    def start(self):
        if not self.running:
            self.timer = Timer(self.config['interval'], self.get_cat_pic)
            self.timer.start()
            self.running = True

    def stop(self):
        self.timer.cancel()
