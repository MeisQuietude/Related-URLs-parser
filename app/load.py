import asyncio
from collections import defaultdict
from typing import Dict, Iterable, Callable, List

from memory_profiler import memory_usage

from app import AppProvider
from app.src import Logger
from app.src.api import API
from app.src.parser import ParserBS, AbstractParser
from app.src.url_representation import AbstractURL, URL


class CLILoadProvider(AppProvider):
    """
    Provider between CLI, API & Database
    """

    # Clear sometimes to optimize memory usage
    urls_map: Dict[str, AbstractURL] = {}
    urls_map_by_depth: Dict[int, List[str]] = defaultdict(list)

    urls_map_is_parsed: Dict[str, bool] = {}

    def __init__(self):
        super().__init__()

        self.async_loop = asyncio.get_event_loop()
        self.bounded_semaphore = \
            asyncio.BoundedSemaphore(self.cli_arguments.bounded_semaphore)
        self.load()

        Logger.info(
            f"Peak memory usage: "
            f"{max(memory_usage(proc=self.load))} MiB"
        )

    def load(self):
        """
        Expected:
        - Load the URL from input and its related URLs
        - Save the loaded data to database
        - Track peak memory usage and execution time
        Allowed parameters (CLI):
        - (-d, --depth) - a depth of parsing URLs
        """
        html_raw = API.get(self.start_url).text
        html_parsed = ParserBS(html_raw)

        url_data = URL(self.start_url, html_parsed)
        self.urls_map[self.start_url] = url_data
        self.urls_map_by_depth[0] = [self.start_url]

        if self.cli_arguments.depth == 0:
            return self.urls_map  # TODO: change return to print function

        related_hrefs = self \
            .get_adjust_related_hrefs(self.start_url, html_parsed)
        url_data._related_urls = related_hrefs
        self.urls_map_by_depth[1] = related_hrefs
        self.urls_map_is_parsed[self.start_url] = True

        self.async_loop.run_until_complete(
            self.start_load_in_depth()
        )

        # TODO: end with print function

    async def start_load_in_depth(self, current_depth: int = 1):
        # TODO: Check for depth == 1 and improve for use with depth == 2
        urls_of_depth = self.urls_map_by_depth[current_depth]
        urls_of_depth_uniq = set(urls_of_depth)

        # Filter already loaded URLs
        urls_to_load = [
            url for url in urls_of_depth_uniq if
            self.urls_map_is_parsed.get(url, None) is None
        ]

        Logger.info(
            f"Requests to load in depth {current_depth} - "
            f"count {len(urls_of_depth)} ("
            f"uniq - {len(urls_of_depth_uniq)}, "
            f"new - {len(urls_to_load)})"
        )

        # Request & parse URLs
        parsed_urls = await \
            self.request_and_parse_related_urls_async(urls_to_load)

        # Save in memory
        for parsed_url in parsed_urls:
            self.urls_map[parsed_url.url] = parsed_url
            self.urls_map_by_depth[current_depth + 1].extend(
                self.get_adjust_related_hrefs(
                    parsed_url.url, parsed_url.html_parsed
                )
            )
            self.urls_map_is_parsed[parsed_url.url] = True

        # Optimize

        # Rerun to depth + 1
        if current_depth < self.cli_arguments.depth:
            await self.start_load_in_depth(current_depth + 1)

    async def request_and_parse_related_urls_async(
        self, urls: Iterable[str]
    ) -> Iterable[URL]:
        responses = await API.fetch_urls_async(urls, self.bounded_semaphore)

        parsed_urls = []
        for response in responses:  # Probably large memory usage here
            url = response.url.__str__()
            html = response.html  # Initialized in API class
            parsed_url = self.map_to_parsed_url(url, html)
            parsed_urls.append(parsed_url)

        return parsed_urls

    def map_to_parsed_url(self, url: str, html: str) -> URL:
        html_parsed = ParserBS(html)
        related_urls = self.get_adjust_related_hrefs(url, html_parsed)
        return URL(
            url=url, html_parsed=html_parsed, related_urls=related_urls)

    def get_adjust_related_hrefs(
        self, url: str, html_parsed: AbstractParser
    ) -> Iterable[str]:
        related_hrefs = CLILoadProvider \
            .get_related_absolute_urls(url, html_parsed)
        related_hrefs = [URL.prepare_url(href) for href in related_hrefs]

        if not self.cli_arguments.allow_external_urls:
            related_hrefs = CLILoadProvider \
                .filter_internal_hrefs(url, related_hrefs)

        return related_hrefs

    @staticmethod
    def get_related_absolute_urls(
        url_src: str, parser: AbstractParser
    ) -> Iterable[str]:
        collection = parser.get_related_anchors_href()
        collection_updated = CLILoadProvider \
            .convert_relative_to_absolute_hrefs(url_src, collection)
        return collection_updated

    @staticmethod
    def convert_relative_to_absolute_hrefs(
        url_src: str, hrefs: Iterable[str]
    ) -> Iterable[str]:
        """
        Convert relative URLs ('/link') to absolute ('https://domain/link')
        """

        # TODO: we should return input type instead of hard return List

        def _convert(href):
            if href.startswith("/"):
                href = url_src + href
            return href

        return [_convert(href) for href in hrefs]

    @staticmethod
    def filter_internal_hrefs(
        url_src: str, hrefs: Iterable[str]
    ) -> Iterable[str]:
        """
        Filter only internal URLs
        """

        # TODO: We should return input type instead of hard return List

        _filter_rule: Callable[[str], bool] = \
            lambda href: href.startswith("/") or href.startswith(url_src)

        return [href for href in hrefs if _filter_rule(href)]

    @staticmethod
    def print_urls_map(urls_map: type(urls_map)):
        print(*(f"{url_str}: {url.title}" for url_str, url in urls_map.items()),
              sep="\n")
