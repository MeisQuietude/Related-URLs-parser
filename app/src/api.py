import asyncio
from typing import Iterable

import aiohttp
import requests

from app.src import Logger


class API(object):
    @staticmethod
    def get(url: str):
        return requests.get(url)

    @staticmethod
    async def fetch_urls_async(
        urls: Iterable[str], bounded_semaphore: asyncio.BoundedSemaphore
    ) -> Iterable[aiohttp.ClientResponse]:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            tasks = [
                API.__async__fetch_url(session, url, bounded_semaphore)
                for url in urls
            ]
            responses: Iterable[aiohttp.ClientResponse] = await asyncio.gather(
                *tasks)
            for response in responses:
                Logger.info(f"{response.url.__str__()} - {response.status}")
                # response.html = await response.text()

            return responses

    @staticmethod
    async def __async__fetch_url(
        session: aiohttp.ClientSession,
        url: str,
        bounded_semaphore: asyncio.BoundedSemaphore
    ) -> aiohttp.ClientResponse:
        async with \
            bounded_semaphore, session.get(url, allow_redirects=True) \
                as response:
            # I should not probably await anything here
            response.html = await response.text(encoding="utf-8")
            return response
