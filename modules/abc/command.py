# -*- coding: utf-8 -*-

from module import Module
from abc import ABC, abstractmethod
from typing import Union
from discord import Message
from discord.abc import Messageable


class Command(ABC):
    def __init__(self, module: Module, name: str):
        if not isinstance(module, Module):
            raise TypeError("module has to inherit Module class")
        self.module = module
        self._name = name.strip().lower()

    @property
    def name(self) -> str:
        """
        User input that triggers the command
        For example when this method returns "cat", the user has to enter "<prefix>cat" to run this command
        @return:
        """
        return self._name

    @abstractmethod
    async def run(self, message: Message, *args, **kwargs):
        """
        The many body of the command, pretty much all the logic belongs here
        @param message: Discord message that triggered the command
        """
        pass

    def help(self) -> Union[str, None]:
        """
        Optional method that gets called when user invoked the help command
        @return: Should be a short description of what the command does
        """
        return None

    def status(self) -> Union[str, None]:
        """
        Message that will be slammed into bot's "Currency Playing" status
        Use {name} placeholder to use the command's name with the right prefix in the status
        @return: Short message that will be displayed in bot's status
        """
        return None

    def validate(self, *args, **kwargs) -> bool:
        """
        Validates if the given input is valid command
        For example if command can upload 5 images at once, but user requests 6. This method should return false
        @return:
        """
        return True


class SendableCommand(Command, ABC):
    @abstractmethod
    async def send(self, channel: Messageable, *args, **kwargs):
        """
        It should be assumed that everything is valid at this point and just have to send the message to the channel
        @param channel: Discord channel where the message should be sent
        """
        pass


class SchedulableCommand(SendableCommand, ABC):
    pass
