import asyncio
import logging
import typing

import yarl
from pydantic.dataclasses import dataclass

from sitemapgen.http_tools.link_fetcher import HttpLinkFetcher
from sitemapgen.utils.url_tools import is_url_reference_to_html_element, is_url_relative, \
    convert_relative_url_to_absolute, \
    is_url_scheme_is_http, get_base_url, is_url_internal


logger = logging.getLogger(__name__)


@dataclass
class ParsePageResult:
    title: str
    links: list[str]


@dataclass
class PageInfo:
    url: str
    title: str
    html: str
    links: list[str]


class IPageParser(typing.Protocol):
    def parse_html(self, raw_html: str) -> ParsePageResult:
        ...


class SiteMapGenerator:
    def __init__(
        self,
        http_link_fetcher: HttpLinkFetcher,
        page_parser: IPageParser,
        on_save_queue: asyncio.Queue[PageInfo]
    ) -> None:
        self._link_fetcher = http_link_fetcher
        self._page_parser = page_parser
        self._on_save_queue = on_save_queue

        self._memory_cache: set[str] = set()

    async def generate_map(self, url: str, depth: int):
        url_ = yarl.URL(url)

        if not url_.is_absolute():
            raise ValueError(f"The input URL is not absolute: {url}")

        next_urls = [url]

        for depth_i in range(depth):
            logger.debug(f"Processing depth {depth_i + 1}...")
            next_urls = await self.get_urls_of(urls=next_urls, init_url_host=url_.host)

        logger.info("Processing is complete")

    async def get_urls_of(self, urls: list[str], init_url_host: str) -> list[str]:
        if not urls:
            return []

        page_info_list: list[typing.Union[BaseException, PageInfo]] = await asyncio.gather(  # type: ignore
            *(self.get_page_result(url=url) for url in urls), return_exceptions=True
        )

        next_urls = []
        for index, page_info in enumerate(page_info_list):
            page_url = urls[index]
            page_base_url = get_base_url(page_url)

            if isinstance(page_info, BaseException):
                logger.error(f"An error occurred during fetch '{page_url}': {str(page_info)}", exc_info=page_info)
                await self.save_page(PageInfo(url=page_url, title=f"[ERROR]: {page_info!s}", html="", links=[]))
                continue

            links = []
            for link in page_info.links:
                if is_url_reference_to_html_element(link) is True:
                    logger.debug(f"Skip reference to HTML element: {link}")
                    continue

                if is_url_relative(link) is True:
                    link = convert_relative_url_to_absolute(url=link, base_url=page_base_url)

                if is_url_scheme_is_http(link) is False:
                    logger.debug(f"Skip not HTTP URL: {link}")
                    continue

                if not is_url_internal(url=link, base_url_host=init_url_host):
                    # TODO: --allow_external
                    logger.debug(f"Skip external URL: {link}")
                    continue

                if link in self._memory_cache:
                    logger.debug(f"Skip cached URL: {link}")

                links.append(link)

            page_info.links = links
            await self.save_page(page_info=page_info)
            next_urls += links

            logger.info(f"Success: {page_url}")

        return next_urls

    async def get_page_result(self, url: str) -> PageInfo:
        page_html = await self._link_fetcher.get_html(url=url)
        parse_info = self._page_parser.parse_html(raw_html=page_html)
        return PageInfo(url=url, title=parse_info.title, html=page_html, links=parse_info.links)

    async def save_page(self, page_info: PageInfo):
        self._memory_cache.add(page_info.url)
        await asyncio.wait_for(self._on_save_queue.put(page_info), 120)
