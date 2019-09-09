# -*- coding: utf-8 -*-
import os
import aiohttp_jinja2
from aiohttp import web
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient


PARSER_PORT = int(os.getenv('PARSER_PORT', 1111))
DB_NAME = os.getenv('MONGO_INITDB_DATABASE')
DB_COLLECTION = os.getenv('MONGO_COLLECTION')
MOTOR_URI = 'mongodb://mongo:{port}/'.format(
    port=os.getenv('MONGO_PORT')
)


class IndexView(web.View):
    """
    Main page, render update parsed data button
    """

    async def _get_last_update(self):
        client = AsyncIOMotorClient(MOTOR_URI)
        collection = client[DB_NAME][DB_COLLECTION]

        latest_post = await collection.find_one(sort=[("created_at", -1)])
        if latest_post and latest_post['created_at']:
            try:
                last_update = datetime.strptime(latest_post['created_at'],
                                                '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                last_update = None

            return last_update

    async def get(self):
        last_update = await self._get_last_update()
        if last_update:
            last_update = last_update.strftime('%Y-%m-%d %H:%M:%S UTC')
        context = {
            'last_update': last_update or 'never made',
            'start_parsing_url': self.request.app.router['start_parsing'].url_for()
        }
        return aiohttp_jinja2.render_template('index.html', self.request, context)
