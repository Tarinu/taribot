# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Union


class Command(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        User input that triggers the command
        For example when this method returns "cat", the user has to enter "<prefix>cat" to run this command
        @return:
        """
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        The many body of the command, pretty much all the logic belongs here
        @return:
        """
        pass

    @classmethod
    def help(cls) -> Union[str, None]:
        """
        Optional method that gets called when user invoked the help command
        @return: Should be a short description of what the command does
        """
        return None

    def validate(self, *args, **kwargs) -> bool:
        """
        Validates if the given input is valid command
        For example if command can upload 5 images at once, but user requests 6. This method should return false
        @return:
        """
        return True
