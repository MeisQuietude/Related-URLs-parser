import logging
import typing

from sqlalchemy.orm import Query

from sitemapgen.db.api_client import DatabaseApiClient, DbTablePage, DbTableSite


logger = logging.getLogger(__name__)


class Observer:
    """ The class for representing the received data """

    def __init__(self, db_client: DatabaseApiClient) -> None:
        self._db = db_client

    def get_related_to_host_links(
        self,
        scheme: str,
        hostname: str,
        port: typing.Optional[int],
        limit: int
    ) -> list[DbTablePage]:
        query_site_criterion = [
            DbTableSite.scheme == scheme,
            DbTableSite.hostname.contains(hostname)
        ]
        if port is not None:
            query_site_criterion.append(DbTableSite.port == port)

        query: Query = (
            self._db.session.query(DbTablePage)
                .join(DbTableSite.ref_pages)
                .filter(*query_site_criterion)
                .order_by(DbTableSite.id, DbTablePage.url_path)
                .limit(limit)
        )
        return [
            result[0] for result in self._db.session.execute(query)
        ]
