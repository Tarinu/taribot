# -*- coding: utf-8 -*-

from __future__ import annotations

import logging as logger
import pathlib
import os
from typing import List
from logging.handlers import RotatingFileHandler


class Config:
    __slots__ = "token", "prefix", "print_messages", "database", "modules", "logging"

    def __init__(self, *, token: str, prefix: str = ";", print_messages: bool = False,
                 database: dict = None, modules: List[dict] = None, logging: dict = None):
        if database is None:
            database = {}
        if modules is None:
            modules = []
        if logging is None:
            logging = {}

        self.__validate_config_type(print_messages, bool, "print_messages has to be boolean")
        self.__validate_config_type(database, dict, "database has to be a dict")
        self.__validate_config_type(modules, list, "modules has to be a list")
        self.__validate_config_type(logging, dict, "logging has to be a dict")

        for module in modules:
            self.__validate_config_type(module, dict, "module has to be dict")
            if not module.get("class"):
                raise ConfigException("module is missing class attribute")

        default_logging = {
            "level": logger.WARNING,
            "format": "[%(asctime)s.%(msecs)03d]:%(levelname)s:%(name)s.%(funcName)s:%(message)s",
            "datefmt": '%Y-%m-%d %H:%M:%S',
            "handlers": [
                logger.StreamHandler(),
                RotatingFileHandler('logs/taribot.log', encoding='utf8', maxBytes=1024 * 1024, backupCount=10)
            ]
        }

        default_logging.update(logging)

        self.token = token
        self.prefix = prefix
        self.print_messages = print_messages
        self.database = database
        self.modules = modules
        self.logging = default_logging

        for handler in self.logging.get("handlers", []):
            if isinstance(handler, logger.FileHandler):
                handler: logger.FileHandler
                pathlib.Path(os.path.dirname(handler.baseFilename)).mkdir(exist_ok=True)

        logger.basicConfig(**self.logging)

    @staticmethod
    def __validate_config_type(variable, variable_type, message: str):
        """
        Tests if the given config variable is correct type

        @raise ConfigException: if it's not valid type
        @param variable:
        @param variable_type:
        @param message: Exception message if the variable is not valid type
        """
        if not isinstance(variable, variable_type):
            raise ConfigException(message)

    @classmethod
    def load(cls, config: dict) -> Config:
        """
        Load external config file into the config object

        @param config:
        @return: cls
        """
        if not isinstance(config, dict):
            raise ConfigException("config has to be dict")
        return cls(**config)


class ConfigException(Exception):
    pass
