from abc import ABC, abstractmethod

import requests
from validator_collection import validators


class AbstractAPI(ABC):
    @staticmethod
    @abstractmethod
    def get(url: str):
        pass


class API(AbstractAPI):
    @staticmethod
    def get(url_raw: str) -> requests.Response:
        """
        Request URL (GET)

        Raises:
             validators.EmptyValueError,
             validators.CannotCoerceError,
             validators.InvalidURLError,
             requests.ConnectionError
        """
        url = validators.url(url_raw)
        response = requests.get(url)
        return response
