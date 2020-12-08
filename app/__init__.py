from abc import ABC

from app.src import args
from app.src.url_representation import URL


class AppProvider(ABC):

    def __init__(self):
        self.cli_arguments = args
        self.start_url = URL.prepare_url(self.cli_arguments.url)
