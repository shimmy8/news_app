# -*- coding: utf-8 -*-
import asyncio
import aiohttp_jinja2
import os
from aiohttp import web
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient


PARSER_PORT = int(os.getenv('PARSER_PORT', 1111))
DB_NAME = os.getenv('MONGO_INITDB_DATABASE', 'news_app')
DB_COLLECTION = os.getenv('MONGO_COLLECTION', 'posts')
MOTOR_URI = 'mongodb://mongo:{port}/'.format(
    port=os.getenv('MONGO_PORT', 27017)
)


class IndexView(web.View):
    """
    Main page, render update parsed data button
    """

    async def _get_last_update(self):
        client = AsyncIOMotorClient(MOTOR_URI)
        collection = client[DB_NAME][DB_COLLECTION]

        latest_post = await collection.find_one(sort=[('created_at', -1)])
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
            'posts_url': self.request.app.router['posts'].url_for(),
            'start_parsing_url': self.request.app.router['start_parsing'].url_for()
        }
        return aiohttp_jinja2.render_template('index.html', self.request, context)


class PostsView(web.View):
    """
    Display JSON posts list
    """
    allowed_query_keys = ('offset', 'limit', 'order')
    order_keys = ('_id', 'title', 'created_at')

    offset = 0
    limit = 5
    max_limit = 150
    order = ['created_at']

    def inspect_quey_params(self, query):
        self._query_errors = []
        for key in iter(query):
            if key in self.allowed_query_keys:
                if key in ['offset', 'limit']:
                    try:
                        value = int(query.get(key))
                    except ValueError:
                        self._query_errors.append(
                            'Wrong {} value. Must be positive integer'.format(key)
                        )
                    else:
                        if value < 0:
                            self._query_errors.append(
                                'Wrong {} value. Must be positive integer'.format(key)
                            )
                        elif key == 'limit' and value > self.max_limit:
                             self._query_errors.append(
                                 'Limit too big. {} maximim allowed.'.format(self.max_limit)
                             )
                        else:
                            setattr(self, key, value)
                elif key == 'order':
                    values = query.get(key).split(',')
                    for value in values:
                        if value in self.order_keys or value.lstrip('-') in self.order_keys:
                            if not value in self.order:
                                self.order.append(value)
                        else:
                            self._query_errors.append(
                                'Wrong order value. Only {} allowed'.format(
                                    ', '.join(self.order_keys))
                            )
            else:
                self._query_errors.append('Unknown query param {}'.format(key))

    async def get(self):
        query = self.request.query
        self.inspect_quey_params(query)
        if self._query_errors:
            return web.Response(text='\n'.join(self._query_errors), status=400)

        client = AsyncIOMotorClient(MOTOR_URI)
        collection = client[DB_NAME][DB_COLLECTION]

        data = []
        sort = [(key.lstrip('-'), -1 if key.startswith('-') else 1) for key in self.order]
        async for item in collection.find(sort=sort, skip=self.offset, limit=self.limit):
            str_id = str(item['_id'])
            item['_id'] = str_id
            data.append(item)
        return web.json_response(data)


class StartParsingView(web.View):
    """
    Send soket message to parsing listener
    """
    seconds_delta = 60

    async def _get_last_parsing_request_date(self):
        client = AsyncIOMotorClient(MOTOR_URI)
        collection = client[DB_NAME]['updates']

        latest_request = await collection.find_one(sort=[('request_date', -1)])
        if latest_request and latest_request['request_date']:
            try:
                request_date = datetime.strptime(latest_request['request_date'],
                                                '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                request_date = None
            return request_date

    async def _add_parsing_request_date(self):
        client = AsyncIOMotorClient(MOTOR_URI)
        collection = client[DB_NAME]['updates']
        return await collection.insert_one({'request_date': datetime.now().isoformat()})

    async def post(self):
        last_update_request = await self._get_last_parsing_request_date()
        delta = self.seconds_delta
        if last_update_request:
            delta = (datetime.now() - last_update_request).seconds

        context = {}
        if delta >= self.seconds_delta:
            reader, writer = await asyncio.open_connection(
                'parser', PARSER_PORT, loop=self.request.app.loop)
            writer.write('parse'.encode())
            writer.close()
            context['message'] = 'Parsing started '+ last_update_request.strftime('%Y-%m-%dT%H:%M:%S.%f')
            await self._add_parsing_request_date()
        else:
            context['message'] = 'Too often... Please, wait for ' + \
                '{} seconds for new parsing request'.format(self.seconds_delta - delta)

        return aiohttp_jinja2.render_template('parsing.html', self.request, context)
