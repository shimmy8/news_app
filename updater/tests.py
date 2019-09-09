# -*- coding: utf-8 -*-
import pytest
from .run import check_item


SAMPLE_ITEM_JSON = '{"url":"http://example.com", "title": "example", "source": "example.com"}'


@pytest.mark.asyncio
async def test_check_item():
    test_passed = await check_item(SAMPLE_ITEM_JSON)
    assert test_passed
