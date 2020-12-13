from abc import ABC

from app.src import args
from app.src.url_representation import URLRepresentation


class AppProvider(ABC):

    def __init__(self):
        self.cli_arguments = args
        self.start_url = URLRepresentation.prepare_url(self.cli_arguments.url)
