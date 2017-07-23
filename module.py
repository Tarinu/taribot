# -*- coding: utf-8 -*-

from event import Event


class Module(object):
    def __init__(self, server):
        self.server = server

    def add_handler(self, event: Event, func: callable):
        """
        Adds the callback function to the list of functions when that event gets called.

        @param event: Type of event
        @param func: Callback function for the event
        """
        self.server.events[event].append(func)
