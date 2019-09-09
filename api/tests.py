# -*- coding: utf-8 -*-
import aiohttp_jinja2
import json
import jinja2
import pytest
from aiohttp import web

from .views import *


@pytest.fixture
def client(loop, aiohttp_client):
    app = web.Application()
    app.router.add_view('/', IndexView, name='index')
    app.router.add_view('/posts', PostsView, name='posts')

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates/'))

    return loop.run_until_complete(aiohttp_client(app))


async def test_index(client):
    resp = await client.get('/')
    assert resp.status == 200


async def test_posts(client):
    fine_response = await client.get('/posts?offset=0&limit=5&order=-title')
    assert fine_response.status == 200

    response_text = await fine_response.text()
    assert isinstance(json.loads(response_text), list)

    offset_error_response = await client.get('/posts?offset=foo')
    assert offset_error_response.status == 400

    limit_error_response = await client.get('/posts?limit=999')
    assert limit_error_response.status == 400

    order_error_response = await client.get('/posts?order=foo')
    assert order_error_response.status == 400
