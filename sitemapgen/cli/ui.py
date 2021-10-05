import asyncio
import enum
import logging
import typing

import typer
import yarl

from sitemapgen.provider import CommandProvider

cli_app = typer.Typer()


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def configure_logging(log_level: LogLevel):
    logging.basicConfig(
        level=log_level.value,
        format="%(asctime)s [%(levelname)-8s] '%(name)s.%(funcName)s:%(lineno)s': %(message)s"
    )


def validate_url(value: str) -> typing.Optional[str]:
    if not value:
        return None

    url = yarl.URL(value.strip().lower())

    if url.host is None:
        raise typer.BadParameter(f"The host '{url.host}' is invalid")
    if url.scheme not in ("http", "https"):
        raise typer.BadParameter(f"The scheme '{url.scheme}' is not allowed")

    return value


@cli_app.command(name="observe", short_help="Observe database data")
def cli_observe(
    url: typing.Optional[str] = typer.Argument(
        default=None,
        file_okay=False,
        dir_okay=False,
        help="The URL to parse its hyperlinks",
        callback=validate_url
    ),
    scheme: typing.Optional[str] = typer.Option(
        None, "-s", "--scheme",
        file_okay=False,
        dir_okay=False,
        help="The URL to parse its hyperlinks"
    ),
    hostname: typing.Optional[str] = typer.Option(
        None, "-h", "--host", "--hostname",
        file_okay=False,
        dir_okay=False,
        help="The URL to parse its hyperlinks"
    ),
    port: typing.Optional[int] = typer.Option(
        None, "-p", "--port",
        file_okay=False,
        dir_okay=False,
        help="The URL to parse its hyperlinks"
    ),
    limit: int = typer.Option(
        50, "-l", "--limit",
        min=0,
        file_okay=False,
        dir_okay=False,
        help="The limit of rows to show (value: 0 is means no limit)"
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.INFO, "--log-level",
        file_okay=False,
        dir_okay=False,
        help="The level of app logging",
        case_sensitive=False,
        callback=lambda v: v.upper(),
    )
):
    configure_logging(log_level=log_level)

    if url is not None:
        return CommandProvider().provide_show_by_url(url=url, limit=limit)

    if scheme is not None and hostname is not None:
        return CommandProvider().provide_show_by_url_params(scheme=scheme, hostname=hostname, port=port, limit=limit)

    raise typer.BadParameter("Neither URL nor scheme with hostname are passed in the parameters")


@cli_app.command(name="generate", short_help="Generate the sitemap", help="Generate the sitemap of entered URL")
def cli_generate(
    url: str = typer.Argument(
        ...,
        file_okay=False,
        dir_okay=False,
        help="The URL to parse its hyperlinks",
        callback=validate_url
    ),
    depth: int = typer.Option(
        1, "-d", "--depth",
        min=1,
        file_okay=False,
        dir_okay=False,
        help="The maximum depth value of hyperlinks on page"
    ),
    concurrent_requests_limit: int = typer.Option(
        6, "--concurrent", "-C",
        min=1,
        file_okay=False,
        dir_okay=False,
        help="The limit of concurrent requests"
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.INFO, "--log-level",
        file_okay=False,
        dir_okay=False,
        help="The level of app logging",
        case_sensitive=False,
        callback=lambda v: v.upper(),
    ),
):
    configure_logging(log_level=log_level)
    asyncio.run(
        CommandProvider().provide_generate(url=url, depth=depth, concurrent_requests_limit=concurrent_requests_limit)
    )
