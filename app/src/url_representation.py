from abc import ABC, abstractmethod
from typing import Iterable

from app.src.parser import AbstractParser


class AbstractURL(ABC):

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @property
    @abstractmethod
    def html_raw(self) -> str:
        pass

    @property
    @abstractmethod
    def html_parsed(self) -> AbstractParser:
        pass

    @property
    @abstractmethod
    def related_urls(self) -> Iterable[str]:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @staticmethod
    def prepare_url(url: str) -> str:
        url_ = url

        if url.endswith("/"):
            url_ = url[:-1]

        return url_


class URL(AbstractURL):

    def __init__(
        self,
        url: str,
        html_parsed: AbstractParser, related_urls: Iterable[str] = None
    ):
        self._url = URL.prepare_url(url)
        self._html_parsed = html_parsed
        self._related_urls = related_urls or []

    @property
    def url(self) -> str:
        return self._url

    @property
    def html_raw(self) -> str:
        return self.html_parsed.__str__()

    @property
    def html_parsed(self) -> AbstractParser:
        return self._html_parsed

    @property
    def related_urls(self) -> Iterable[str]:
        return self._related_urls

    @property
    def title(self):
        return self.html_parsed.title
