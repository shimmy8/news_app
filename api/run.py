# -*- coding: utf-8 -*-
import os
import aiohttp_jinja2
import jinja2
from aiohttp import web

from views import *


API_PORT = int(os.getenv('API_PORT', 3000))


def run():
    app = web.Application()

    app.router.add_view('/', IndexView, name='index')

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates/'))

    web.run_app(app, port=API_PORT)


if __name__ == '__main__':
    run()
