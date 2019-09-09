# -*- coding: utf-8 -*-
import asyncio

from .parser import NewsCrawler


TEST_ITEM = {
    'url': 'http://example.com',
    'title': 'example',
    'source': 'example.com'
}
SAMPLE_DATA = """
<table class="itemlist">
    <tr class="athing">
        <td>
            <a class="storylink" href="{url}">{title}</a>
            <span class="sitestr">{source}</span>
        </td>
    </tr>
</table>
""".format(**TEST_ITEM)


async def test_parser():
    loop = asyncio.get_event_loop()

    crawler = NewsCrawler(loop)
    items = crawler.parse_results(SAMPLE_DATA)
    for item in items:
        assert item == TEST_ITEM
