from typing import Iterable

import requests
from aiohttp import ClientSession

from app.src import Logger
from app.src.validator import Validator


class API(object):

    @staticmethod
    def get(url: str) -> requests.Response:
        """
        Request URL (GET)
        """
        try:
            response = requests.get(url)
            return response
        except Exception as error:
            Logger.warning(
                f"Request to `{url} failed due to error: {error.__str__()}`"
            )


class API(object):

    async def get_all(self, urls: Iterable[str]):
        async with ClientSession() as session:
            try:
                Validator.is_valid_email()
            except Exception as error:
                session.request(method='GET', url=url)
                pass
