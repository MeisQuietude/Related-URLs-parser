from abc import ABC, abstractmethod
from functools import cached_property
from typing import Set, Iterable

from bs4 import BeautifulSoup, ResultSet


class AbstractParser(ABC):
    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def anchor_nodes(self) -> Iterable:
        pass

    @abstractmethod
    def get_related_anchors_href(self) -> Iterable[str]:
        pass

    @staticmethod
    def _is_href_url_related(url: str) -> bool:
        return not (
            url is None or
            url.startswith('#') or
            url == '/'
        )


class ParserBS(AbstractParser):
    """
    The custom parser over BeautifulSoup
    """

    def __init__(self, html_raw: str, parser_bs_type: str = "html.parser"):
        self.html_parsed = BeautifulSoup(html_raw, parser_bs_type)

    @property
    def html_raw(self) -> str:
        return self.html_parsed.__str__()

    @cached_property
    def title(self) -> str:
        title = self.html_parsed.find("title")
        return title and title.text or ""

    @cached_property
    def anchor_nodes(self) -> Iterable[ResultSet]:
        return self.html_parsed.find_all("a", attrs={"href": True})

    def get_related_anchors_href(self) -> Iterable[str]:
        collection: Set[str] = set()

        for node in self.anchor_nodes:
            href: str = node.attrs.get("href")
            if not ParserBS._is_href_url_related(href):
                continue
            collection.add(href)

        return collection

    def __repr__(self):
        return self.html_parsed.__repr__()
