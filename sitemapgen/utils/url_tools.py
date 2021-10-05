import typing
import urllib.parse

import yarl


def is_url_reference_to_html_element(url: str) -> bool:
    return url.startswith("#")


def is_url_scheme_is_http(url: str) -> bool:
    return url.startswith("http")


def is_url_relative(url: str) -> bool:
    return url.startswith("/")


def is_url_internal(url: str, base_url_host: str) -> bool:
    curr = yarl.URL(url)
    return curr.host.endswith(base_url_host)


def convert_relative_url_to_absolute(url: str, base_url: str) -> str:
    return urllib.parse.urljoin(base=base_url, url=url)


def build_base_url(scheme: str, hostname: str, port: typing.Optional[typing.Union[int, str]] = None) -> str:
    if port is not None:
        return f"{scheme}://{hostname}:{port}"

    return f"{scheme}://{hostname}"


def get_base_url(url: str) -> str:
    absolute_url = yarl.URL(url)

    if not absolute_url.is_absolute():
        raise ValueError(f"The URL is not absolute for get base of it: {url}")

    return build_base_url(scheme=absolute_url.scheme, hostname=absolute_url.host, port=absolute_url.port)
