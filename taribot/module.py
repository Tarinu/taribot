# -*- coding: utf-8 -*-

from __future__ import annotations
import taribot.modules.abc
from taribot.event import Event
from abc import ABC


class Module(ABC):
    def __init__(self, server):
        self._server = server

    @property
    def server(self):
        return self._server

    def add_handler(self, event: Event, func: callable):
        """
        Adds the callback function to the list of functions when that event gets called.

        @param event: Type of event
        @param func: Callback function for the event
        """
        self.server.add_event(event, func)

    def add_command(self, command: taribot.modules.abc.Command):
        self.server.add_command(command)
