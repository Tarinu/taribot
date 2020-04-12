#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from taribot.server import Server
from taribot.config import Config
from config import config

if __name__ == '__main__':
    Server(Config.load(config)).run()
