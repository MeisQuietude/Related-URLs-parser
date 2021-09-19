import asyncio
import logging
import typing
from functools import cached_property
from urllib.parse import urljoin

import aiohttp
import yarl

from sitemapgen.cmds.generate_map import SiteMapGenerator, IPageParser, PageInfo
from sitemapgen.cmds.observer import Observer
from sitemapgen.db.api_client import DatabaseApiClient, DbTableSite, DbTablePage
from sitemapgen.http_tools.link_fetcher import HttpLinkFetcher
from sitemapgen.settings import Settings
from sitemapgen.utils.html_page_parser import LxmlParser
from sitemapgen.utils.url_tools import build_base_url

logger = logging.getLogger(__name__)


class CommandProvider:
    def __init__(self) -> None:
        self._settings = Settings()
        self._stop_event = asyncio.Event()

    def provide_show_by_url(self, url: str, limit: int) -> None:
        url = yarl.URL(url)

        if not url.host:
            raise ValueError("Incorrect URL")

        return self.provide_show_by_url_params(scheme=url.scheme, hostname=url.host, port=url.port, limit=limit)

    def provide_show_by_url_params(self, scheme: str, hostname: str, port: typing.Optional[int], limit: int) -> None:
        page_list = self.observer.get_related_to_host_links(scheme=scheme, hostname=hostname, port=port, limit=limit)

        self.provide_show(page_list=page_list)

    def provide_show(self, page_list: list[DbTablePage]) -> None:
        for i, page in enumerate(page_list):
            base_url = build_base_url(scheme=page.ref_site.scheme, hostname=page.ref_site.hostname)
            url = urljoin(base_url, page.url_path)
            logger.info(f"{i + 1:4d}. {url} : {page.title}")

    async def provide_generate(self, url: str, depth: int, concurrent_requests_limit: int) -> None:
        site_map_queue: asyncio.Queue[PageInfo] = asyncio.Queue()

        smc = SiteMapGenerator(
            http_link_fetcher=self.http_link_fetcher,
            page_parser=self.page_parser,
            on_save_queue=site_map_queue
        )

        try:
            asyncio.ensure_future(self._run_saving_page_info(site_map_queue))
            await smc.generate_map(url=url, depth=depth)
        finally:
            await self.graceful_shutdown()

            retries = 0
            while not site_map_queue.empty():
                await asyncio.sleep(0.5)

                if retries > 15:
                    raise RuntimeError(
                        f"Unknown error during saving pages to database: qsize = {site_map_queue.qsize()}"
                    )

                retries += 1

    async def _run_saving_page_info(self, site_map_queue: asyncio.Queue[PageInfo]):
        while True:
            try:
                page_info_to_save = await asyncio.wait_for(site_map_queue.get(), 1)
                await self._save_page_info(page_info=page_info_to_save)
            except asyncio.TimeoutError:
                if self._stop_event.is_set():
                    return

    async def _save_page_info(self, page_info: PageInfo):
        logger.debug(f"Saving {page_info.url}...")
        url = yarl.URL(page_info.url)

        query_site_criterion = (
            DbTableSite.scheme == url.scheme,
            DbTableSite.hostname == url.host,
            DbTableSite.port == url.port
        )

        get_page_query = (
            self.db_api_client.session.query(DbTablePage)
                .join(DbTableSite.ref_pages)
                .filter(*query_site_criterion, DbTablePage.url_path == url.path)
        )
        # Update orw
        if (page := get_page_query.scalar()) is not None:
            if page.title != page_info.title or page.html != page_info.html:
                page.title = page_info.title
                page.html = page_info.html
                self.db_api_client.session.add(page)
                self.db_api_client.session.commit()
            return

        # Create row
        page = DbTablePage(
            url_path=url.path,
            title=page_info.title,
            html=page_info.html
        )

        site: typing.Optional[DbTableSite] = (
            self.db_api_client.session
                .query(DbTableSite)
                .filter(*query_site_criterion)
                .scalar()
        )
        if site is not None:
            page.ref_site = site
        else:
            created_site = DbTableSite(scheme=url.scheme, hostname=url.host, port=url.port)
            page.ref_site = created_site

        self.db_api_client.session.add(page)
        self.db_api_client.session.commit()

    async def graceful_shutdown(self):
        await self.client_session.close()
        self._stop_event.set()

    @cached_property
    def page_parser(self) -> IPageParser:
        return LxmlParser()

    @cached_property
    def observer(self) -> Observer:
        return Observer(db_client=self.db_api_client)

    @cached_property
    def db_api_client(self) -> DatabaseApiClient:
        pg_settings = self._settings.postgres
        return DatabaseApiClient(
            host=pg_settings.hostname,
            port=pg_settings.port,
            database=pg_settings.database,
            username=pg_settings.username,
            password=pg_settings.password,
        )

    @cached_property
    def http_link_fetcher(self) -> HttpLinkFetcher:
        return HttpLinkFetcher(client_session=self.client_session)

    @cached_property
    def client_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            connector=self.client_session_connector,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"},
            cookie_jar=aiohttp.DummyCookieJar()
        )

    @cached_property
    def client_session_connector(self) -> aiohttp.BaseConnector:
        return aiohttp.TCPConnector()
