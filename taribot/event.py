# -*- coding: utf-8 -*-

from enum import Enum, auto


class Event(Enum):
    """
    Supported event types
    """
    ON_READY = auto()
    ON_MESSAGE = auto()
    ON_MESSAGE_DELETE = auto()

    @classmethod
    def has_value(cls, value):
        return any(value == item for item in cls)
