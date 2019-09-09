# -*- coding: utf-8 -*-
import asyncio
import datetime
import json
import logging
import os
import re
import motor.motor_asyncio


UPDATER_PORT = int(os.getenv('UPDATER_PORT', 1112))
DB_NAME = os.getenv('MONGO_INITDB_DATABASE')
DB_PORT = os.getenv('MONGO_PORT')
DB_COLLECTION = os.getenv('MONGO_COLLECTION')


DATA_VALUES_TESTS = {
    'url': re.compile(r'http(s)?://(www\.)?[a-zA-Z-0-9-/\.\-\%\?\=&]+'),
    'title': re.compile(r'\w{1,}'),
    'source': re.compile(r'\w{1,}')
}


async def check_item(item):
    try:
        loaded_item = json.loads(item)
    except Exception as e:
        logging.error('Exception while loading JSON item: {}'.format(e))
        return
    valid = True
    for key, value in loaded_item.items():
        if key in DATA_VALUES_TESTS:
            if value and not DATA_VALUES_TESTS[key].match(value):
                logging.error('Value format mismatch: {} - {}'.format(key, value))
                valid = False
        else:
            logging.error('Unknown item key: {}'.format(key))
            valid = False
    if valid:
        return loaded_item


async def save_loaded_item(item):
    motor_uri = 'mongodb://mongo:{port}'.format(
        port=DB_PORT
    )

    client = motor.motor_asyncio.AsyncIOMotorClient(motor_uri)
    db = client[DB_NAME]
    collection = db[DB_COLLECTION]

    found_item = await collection.find_one({'url': item['url']})
    if found_item:
        return await collection.update_one(found_item, {'$set': item})
    else:
        item['created_at'] = datetime.datetime.utcnow().isoformat()
        return await collection.insert_one(item)


async def recive_item(reader, writer):
    data = await reader.read(4096)
    message = data.decode()

    item = await check_item(message)
    if item:
        await save_loaded_item(item)


async def run():
    server = await asyncio.start_server(recive_item, 'updater', UPDATER_PORT)

    addr = server.sockets[0].getsockname()
    print(f'Listening {addr}')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(run())
