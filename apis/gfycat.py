# -*- coding: utf-8 -*-

import aiohttp
import json
from random import choice


class Gfycat(object):
    def __init__(self, config: dict):
        self.config = config
        self.token = None  # type: dict
        self.header = None  # type: dict
        self.session = aiohttp.ClientSession()
        self.gfycats = None  # type: dict

    async def get_token(self):
        async with self.session.post('https://api.gfycat.com/v1/oauth/token', data=json.dumps(self.config.get('token_data'))) as token:
            assert token.status == 200
            self.token = await token.json()
            self.header = {'Authorization': 'Bearer ' + self.token.get('access_token')}

    async def get_album_gfycats(self):
        async with self.session.get('https://api.gfycat.com/v1/me/albums/'+self.config['album_id'],
                                    headers=self.header) as resp:
            result = await resp.json()
            self.gfycats = result.get('publishedGfys')

    async def get_random_gfycat(self):
        if self.gfycats is None:
            await self.get_token()
            await self.get_album_gfycats()
        return "https://gfycat.com/" + choice(self.gfycats).get('gfyName')
