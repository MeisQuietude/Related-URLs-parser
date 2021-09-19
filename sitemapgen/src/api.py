import asyncio
from typing import Iterable

import aiohttp
import requests
from aiohttp import ClientTimeout

from sitemapgen.src import Logger


class API(object):
    @staticmethod
    def get(url: str):
        try:
            return requests.get(url)
        except Exception as error:
            Logger.error(
                f"Unable to get `{url}` due to error: {type(error)}"
            )

    @staticmethod
    async def fetch_urls_async(
        urls: Iterable[str], bounded_semaphore: asyncio.BoundedSemaphore
    ) -> Iterable[aiohttp.ClientResponse]:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                ssl=None,
                enable_cleanup_closed=True
            ),
            timeout=ClientTimeout(10),
        ) as session:
            tasks = [
                API.__async__fetch_url(session, url, bounded_semaphore)
                for url in urls
            ]
            responses: Iterable[aiohttp.ClientResponse] = \
                await asyncio.gather(*tasks)

            return responses

    @staticmethod
    async def __async__fetch_url(
        session: aiohttp.ClientSession,
        url: str,
        bounded_semaphore: asyncio.BoundedSemaphore
    ) -> aiohttp.ClientResponse:
        try:
            async with \
                bounded_semaphore, session.get(
                url, allow_redirects=True, timeout=ClientTimeout(10)
            ) \
                as response:
                # I should not probably await anything here
                response.html = await response.text(encoding="utf-8")
                Logger.info(f"{response.url.__str__()} - {response.status}")

                return response
        except Exception as error:
            Logger.error(f"Unable to get `{url}` due to error: {error}")
