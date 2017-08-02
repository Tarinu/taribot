#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from server import Server
import logging


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING,
                        format="[%(asctime)s.%(msecs)03d]:%(levelname)s:%(name)s.%(funcName)s:%(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S')
    Server().run()
