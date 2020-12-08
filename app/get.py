from app import AppProvider


class CmdGetProvider(AppProvider):
    def __init__(self):
        super().__init__()

    def get(self):
        """
        Expected:
        - Get the data (url, title) of related URLs from database
        Allowed parameters (CLI):
        - (-n, --limit) - a number of URLs
        """
        pass
