#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from server import Server
import logging.handlers
import pathlib

if __name__ == '__main__':
    pathlib.Path('logs').mkdir(exist_ok=True)
    logging.basicConfig(level=logging.WARNING,
                        format="[%(asctime)s.%(msecs)03d]:%(levelname)s:%(name)s.%(funcName)s:%(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[
                            logging.StreamHandler(),
                            logging.handlers.RotatingFileHandler('logs/taribot.log', encoding='utf8', maxBytes=1024 * 1024, backupCount=10)
                        ])
    Server().run()
