import asyncio
from collections import defaultdict
from typing import Dict, Iterable, List

from sitemapgen import AppProvider
from sitemapgen.src import Logger, session
from sitemapgen.src.api import API
from sitemapgen.src.dbapi import ModelURL
from sitemapgen.src.metrics import get_time_mem_metric
from sitemapgen.src.parser import ParserBS, AbstractParser
from sitemapgen.src.url_representation import AbstractURLRepresentation, \
    URLRepresentation
from sitemapgen.src.url_serializer import URLSerializer
from sitemapgen.src.utils import Utils


class CLILoadProvider(AppProvider):
    """
    Provider between CLI, API & Database
    """

    parser: AbstractParser = ParserBS

    urls_map: Dict[str, AbstractURLRepresentation] = {}
    urls_map_by_depth: Dict[int, List[str]] = defaultdict(list)
    urls_map_is_parsed: Dict[str, bool] = {}

    def __init__(self):
        super().__init__()

        self.async_loop = asyncio.get_event_loop()
        self.bounded_semaphore = \
            asyncio.BoundedSemaphore(self.cli_arguments.bounded_semaphore)

        self.load()

    @get_time_mem_metric
    def load(self):
        """
        Expected:
        - Load the URL from input and its related URLs
        - Save the loaded data to database
        - Track peak memory usage and execution time
        Allowed parameters (CLI):
        - (-d, --depth) - a depth of parsing URLs
        """
        response = API.get(self.start_url)
        if response is None:
            Logger.error("Please check URL and retry later...")
            return

        html_raw = response.text
        html_parsed = self.parser(html_raw)

        url_data = URLRepresentation(self.start_url, html_parsed)
        self.urls_map[self.start_url] = url_data
        self.urls_map_by_depth[0] = [self.start_url]

        ModelURL.upsert(
            **URLSerializer(
                url_data.url,
                url_data.title,
                url_data.html_raw
            ).__repr__()
        )
        session.commit()

        if self.cli_arguments.depth == 0:
            return

        related_hrefs = self \
            .get_adjust_related_hrefs(self.start_url, html_parsed)
        url_data._related_urls = related_hrefs
        self.urls_map_by_depth[1] = related_hrefs
        self.urls_map_is_parsed[self.start_url] = True

        self.async_loop.run_until_complete(
            self.start_load_in_depth()
        )

    async def start_load_in_depth(self, current_depth: int = 1):
        Logger.info(f"Compute load in depth {current_depth}"
                    f", please wait a couple of time...")

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

        # Memory optimization
        batch_limit = 100
        for batch_offset in range(len(urls_to_load) // batch_limit + 1):
            start = batch_offset * batch_limit
            end = start + batch_limit
            batch_to_load = urls_to_load[start:end]

            # Request & parse URLs
            parsed_urls = await \
                self.request_and_parse_related_urls_async(batch_to_load)

            # Save in memory & db
            for url in set(parsed_urls):

                parsed_url = self.urls_map.get(url, None)
                if parsed_url is None:
                    # Check the store in DB
                    q_ = session.query(ModelURL) \
                        .filter(ModelURL.name == url) \
                        .limit(1)
                    for record in q_:
                        parsed_url = self.parser(record.html)
                        self.urls_map[url] = URLRepresentation(url, parsed_url)
                        break
                    else:
                        Logger.error(f"Something wrong with {url}")

                self.urls_map_by_depth[current_depth + 1].extend(
                    self.get_adjust_related_hrefs(
                        url, parsed_url.html_parsed
                    )
                )
                self.urls_map_is_parsed[url] = True

                ModelURL.upsert(
                    **URLSerializer(
                        url, parsed_url.title, parsed_url.html_raw
                    ).__repr__()
                )

                del self.urls_map[url]
            session.commit()

        del self.urls_map_by_depth[current_depth]

        # Rerun to depth + 1
        if current_depth < self.cli_arguments.depth:
            await self.start_load_in_depth(current_depth + 1)

    async def request_and_parse_related_urls_async(
        self, urls: Iterable[str]
    ) -> Iterable[str]:
        responses = await API.fetch_urls_async(urls, self.bounded_semaphore)

        parsed_urls = []
        for response in responses:  # Probably large memory usage here
            if response is None:
                continue
            url = URLRepresentation.prepare_url(response.url.__str__())
            html = response.html  # Initialized in API class

            self.parse_memsave_url(url, html)

            parsed_urls.append(url)

        return parsed_urls

    def parse_memsave_url(self, url: str, html: str) -> URLRepresentation:
        """
        Create ParserURL object and store it in memory
        """
        html_parsed = self.parser(html)
        related_urls = self.get_adjust_related_hrefs(url, html_parsed)

        parsed_url = URLRepresentation(
            url=url, html_parsed=html_parsed, related_urls=related_urls
        )
        self.urls_map[url] = parsed_url

        return parsed_url

    def get_adjust_related_hrefs(
        self, url: str, html_parsed: AbstractParser
    ) -> Iterable[str]:
        return Utils.get_adjust_related_hrefs(
            url=url,
            html_parsed=html_parsed,
            allow_external_urls=self.cli_arguments.allow_external_urls
        )
