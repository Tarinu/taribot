# -*- coding: utf-8 -*-

import logging.handlers

# config is set up to show the default values
config = {
    "token": "",  # Required
    "prefix": ";",
    "print_messages": False,  # If the bot should write incoming messages to console/stdout
    "database": {  # Database is set up using sqlite
        "enabled": False,
        "database": "taribot.db"
    },
    "logging": {  # logging gets passed to logging.basicConfig, for more info about it check out python docs
        "level": logging.WARNING,
        "format": "[%(asctime)s.%(msecs)03d]:%(levelname)s:%(name)s.%(funcName)s:%(message)s",
        "datefmt": '%Y-%m-%d %H:%M:%S',
        "handlers": [
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler('logs/taribot.log', encoding='utf8', maxBytes=1024 * 1024, backupCount=10)
        ]
    },
    "modules": [
        {
            "class": "Kitty",
            "enabled": False,
            "keyword": "cat",
            "location": "/srv/taribot",  # Location of images in the local filesystem
            "max_images": 5,
            "gfycat": {
                "enabled": False,
                "keyword": "catvid",
                "album_id": "",
                "token_data": {
                    "client_id": "",
                    "client_secret": "",
                    "username": "",
                    "password": "",
                    "grant_type": "password"  # Only supports password currently
                }
            }
        },
        {
            "class": "Scheduler",
            "enabled": False,
            "keyword": "schedule",
            "remove_keyword": "unschedule"
        }
    ]
}
