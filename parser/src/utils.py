from typing import Iterable, Callable

from parser import URLRepresentation
from parser.src.parser import AbstractParser


class Utils(object):
    """
    Some methods that connect URLs and parsed HTML
    """

    @staticmethod
    def get_adjust_related_hrefs(
        url: str, html_parsed: AbstractParser, allow_external_urls=False
    ) -> Iterable[str]:
        """
        Get related URLs from parsed HTML and adjust them
        """
        related_hrefs = Utils \
            .get_related_absolute_urls(url, html_parsed)
        related_hrefs = [URLRepresentation.prepare_url(href) for href in related_hrefs]

        if not allow_external_urls:
            related_hrefs = Utils \
                .filter_internal_hrefs(url, related_hrefs)

        return related_hrefs

    @staticmethod
    def get_related_absolute_urls(
        url_src: str, parser: AbstractParser
    ) -> Iterable[str]:
        """
        Get related URLs from parsed HTML and convert them into absolute
        """
        collection = parser.get_related_anchors_href()

        collection_updated = Utils \
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

        def _convert(href: str) -> str:
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
