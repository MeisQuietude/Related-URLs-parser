import asyncio
import logging
import ssl
import typing

import aiohttp
import backoff
import yarl

from sitemapgen.http_tools.backoff_utils import log_backoff, log_giveup


class HttpLinkFetcher:
    def __init__(self, client_session: aiohttp.ClientSession) -> None:
        self._session = client_session

    async def get_html(self, url: typing.Union[str, yarl.URL], **request_kwargs) -> str:
        url_ = url
        if not isinstance(url, yarl.URL):
            url_ = yarl.URL(url)

        if not url_.host or url_.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL: {url}")

        async with await self._request(url=url, method=aiohttp.hdrs.METH_GET, **request_kwargs) as response:
            return await response.text(encoding='utf-8')

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(
            ConnectionResetError,
            aiohttp.ClientPayloadError,
            asyncio.TimeoutError,
            asyncio.IncompleteReadError,
            ssl.SSLError,
        ),
        max_time=120,
        jitter=backoff.full_jitter,
        logger=__name__,
        on_backoff=log_backoff,
        on_giveup=log_giveup,
        backoff_log_level=logging.DEBUG,
        giveup_log_level=logging.WARNING
    )
    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=aiohttp.ClientConnectionError,
        max_time=10,
        jitter=backoff.full_jitter,
        logger=__name__,
        on_backoff=log_backoff,
        on_giveup=log_giveup,
        backoff_log_level=logging.DEBUG,
        giveup_log_level=logging.WARNING
    )
    async def _request(self, url: str, method: str = aiohttp.hdrs.METH_GET, **request_kwargs) -> aiohttp.ClientResponse:
        return await self._session.request(method, url, **request_kwargs)
