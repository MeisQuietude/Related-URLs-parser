from abc import ABC, abstractmethod
from functools import cached_property
from typing import Iterator

from bs4 import BeautifulSoup, ResultSet


class AbstractParser(ABC):
    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def anchor_nodes(self) -> Iterator:
        pass


class ParserBS(AbstractParser):
    """
    The custom parser over BeautifulSoup
    """

    def __init__(self, html_raw: str, parser_bs_type: str = "html.parser"):
        self.html_raw = html_raw
        self.html_parsed = BeautifulSoup(html_raw, parser_bs_type)

    @cached_property
    def title(self):
        return self.html_parsed.find("title").text

    @cached_property
    def anchor_nodes(self) -> ResultSet:
        return self.html_parsed.find_all("a", attrs={"href": True})

    def __repr__(self):
        return self.html_parsed.__repr__()
