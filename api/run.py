# -*- coding: utf-8 -*-
import os
from aiohttp import web

from views import *


API_PORT = int(os.getenv('API_PORT', 3000))


def run():
    app = web.Application()
    web.run_app(app, port=API_PORT)


if __name__ == '__main__':
    run()
