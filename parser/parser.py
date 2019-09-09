# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import logging
from lxml import html


class NewsCrawler:
    start_url = 'https://news.ycombinator.com'

    def __init__(self, loop):
        self.loop = loop

    async def fetch(self, url):
        """
        Get HTML data from start url
        """
        logging.info('Fetching: {}'.format(url))
        try:
            session = aiohttp.ClientSession(loop=self.loop)
            async with session.get(url) as response:
                html = await response.read()
            await session.close()
            return html
        except Exception as e:
            logging.error('Error: {}'.format(e))

    def parse_results(self, data):
        """
        Parse HTML data with xpath selectors
        """
        html_data = html.fromstring(data)
        for row in html_data.xpath('//table[@class="itemlist"]//tr[@class="athing"]'):
            title_link = row.xpath('.//a[@class="storylink"]')[0]
            site_str = row.xpath('.//span[@class="sitestr"]')
            yield {
                'url': title_link.xpath('@href')[0],
                'title': title_link.text,
                'source': site_str[0].text if site_str else None
            }

    async def crawl(self):
        data = await self.fetch(self.start_url)
        try:
            results = self.parse_results(data)
        except Exception as e:
            logging.error('Parsing error: {}'.format(e))
            results = []

        return results


def parse():
    loop = asyncio.get_event_loop()

    crawler = NewsCrawler(loop)
    future = asyncio.Task(crawler.crawl())

    loop.run_until_complete(future)

    loop.close()
