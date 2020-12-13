from sqlalchemy.orm import Query

from app import AppProvider, URLRepresentation
from app.src import session, Logger
from app.src.dbapi import ModelURL
from app.src.parser import ParserBS, AbstractParser
from app.src.utils import Utils


class CmdGetProvider(AppProvider):
    parser: AbstractParser = ParserBS

    def __init__(self):
        super().__init__()
        self.get()

    def get(self):
        """
        Expected:
        - Get the data (url, title) of related URLs from database
        Allowed parameters (CLI):
        - (-n, --limit) - a number of URLs
        """
        url_input = URLRepresentation.prepare_url(self.cli_arguments.url)

        query: Query = session.query(
            ModelURL.name, ModelURL.title, ModelURL.html
        ) \
            .filter(ModelURL.name == url_input) \
            .limit(1)

        for url in query:
            Logger.info(f"Get related URLs for {url.name}: {url.title}")

            html_parsed = self.parser(url.html)
            related_urls = Utils.get_adjust_related_hrefs(url.name, html_parsed)
            query_related = session.query(
                ModelURL.name, ModelURL.title, ModelURL.html
            ) \
                .filter(ModelURL.name.in_(related_urls))

            if self.cli_arguments.limit > 0:
                query_related = query_related.limit(self.cli_arguments.limit)

            for related_url in query_related:
                Logger.info(f"{related_url.name}: {related_url.title}")

            break
        else:
            Logger.info("No loaded info for this URL. Try to load it first...")

        # this_url = query[0]

        # if self.cli_arguments.limit > 0:
        #     query = query.limit(self.cli_arguments.limit)

        # URL(url_input)
        # Utils.get_adjust_related_hrefs()

        # for name, title in query:
        #     Logger.info(f"{name}: {title}")
