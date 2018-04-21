# -*- coding: utf-8 -*-

import aiohttp
from random import choice


class Gfycat(object):
    def __init__(self, config: dict):
        self.config = config
        self.token = None  # type: dict
        self.header = None  # type: dict
        self.session = None  # type: aiohttp.ClientSession
        self.gfycats = None  # type: dict

    def before_request(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def get_token(self):
        self.before_request()
        async with self.session.post('https://api.gfycat.com/v1/oauth/token', json=self.config.get('token_data')) as token:
            assert token.status == 200
            self.token = await token.json()
            self.header = {'Authorization': 'Bearer ' + self.token.get('access_token')}

    async def get_album_gfycats(self):
        self.before_request()
        async with self.session.get('https://api.gfycat.com/v1/me/albums/'+self.config['album_id'],
                                    headers=self.header) as resp:
            result = await resp.json()
            if resp.status == 200:
                self.gfycats = result.get('publishedGfys')
            else:
                raise Exception(result.get('message'))

    async def get_random_gfycat(self):
        if self.gfycats is None:
            await self.get_token()
            await self.get_album_gfycats()
        return "https://gfycat.com/" + choice(self.gfycats).get('gfyName')

