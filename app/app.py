from typing import Dict, Iterable, Callable

from app.src import Logger
from app.src.api import API
from app.src.cli import args
from app.src.parsed_url import AbstractParsedURL, ParsedURL
from app.src.parser import ParserBS, AbstractParser

global_context = {}


class AppProvider(object):
    """
    Provider between CLI, API & Database
    """
    urls_parsed: Dict[str, bool] = {}
    urls_map: Dict[str, AbstractParsedURL] = {}

    def __init__(self, start_url: str, depth: int):
        self.start_url = start_url
        if self.start_url.endswith("/"):
            self.start_url = self.start_url[:-1]

        self.depth = depth

    def load(self) -> type(urls_map):
        """
        Expected:
        - Load the URL from input and its related URLs
        - Save the loaded data to database
        - Track peak memory usage and execution time
        Allowed parameters (CLI):
        - (-d, --depth) - a depth of parsing URLs
        """
        html_raw = AppProvider.request_html(self.start_url)
        html_parsed = ParserBS(html_raw)

        url_data = ParsedURL(self.start_url, html_parsed)
        self.urls_map[self.start_url] = url_data

        if self.depth == 0:
            return self.urls_map

        related_hrefs = self.parse_related_hrefs(html_parsed)
        url_data._related_urls = related_hrefs
        self.urls_parsed[self.start_url] = True

        parsed_url = self.load_url(self.start_url)
        self.load_related_urls(parsed_url, self.depth)

        return self.urls_map

    def get(self):
        """
        Expected:
        - Get the data (url, title) of related URLs from database
        Allowed parameters (CLI):
        - (-n, --limit) - a number of URLs
        """
        pass

    def load_related_urls(self, url: AbstractParsedURL, current_depth: int = 1):
        for href in url.related_urls:
            Logger.debug(f"Request to {href} ...")
            parsed_url = self.load_url(href)
            if current_depth < self.depth:
                self.load_related_urls(parsed_url, current_depth + 1)

    def load_url(self, href: str) -> AbstractParsedURL:
        if self.urls_parsed.get(href, None) is not None:
            return self.urls_map[href]

        html_raw = AppProvider.request_html(href)
        html_parsed = ParserBS(html_raw)
        related_hrefs = self.parse_related_hrefs(html_parsed)
        url_ = ParsedURL(href, html_parsed, related_hrefs)

        self.urls_map[href] = url_
        self.urls_parsed[href] = True

        return url_

    def parse_related_hrefs(self, html_parsed: AbstractParser):
        related_hrefs = AppProvider \
            .get_related_absolute_urls(self.start_url, html_parsed)

        if not args.allow_external_urls:
            related_hrefs = AppProvider \
                .filter_internal_hrefs(self.start_url, related_hrefs)

        return related_hrefs

    @staticmethod
    def request_html(url: str) -> str:
        try:
            response = API.get(url)
            if response.ok:
                return response.text
            raise Exception("Response is not ok")

        except Exception as error:
            print(f"Request to {url} failed...")

    @staticmethod
    def get_related_absolute_urls(
        url_src: str, parser: AbstractParser
    ) -> Iterable[str]:
        collection = parser.get_related_anchors_href()
        collection_updated = AppProvider \
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


def main():
    app = AppProvider(
        start_url=args.url,
        depth=args.depth
    )
    if args.method == 'get':
        return app.get()
    if args.method == 'load':
        result = app.load()
        return AppProvider.print_urls_map(result)

    print(f"Expected method: 'get', 'load'. Got: '{args.method}'")
