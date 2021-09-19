import lxml.etree
import lxml.html

from sitemapgen.cmds.generate_map import ParsePageResult


class LxmlParser:

    def parse_html(self, raw_html: str) -> ParsePageResult:
        parsed_html = lxml.html.fromstring(raw_html)

        title = self.get_title(html=parsed_html)
        links = self.get_links(html=parsed_html)

        return ParsePageResult(title=title, links=links)

    def get_title(self, html: lxml.html.HtmlElement) -> str:
        elements = html.xpath("/html/head/title")

        if elements:
            if element := elements[0].text:
                return element

        return "No title"

    def get_links(self, html) -> list[str]:
        elements = html.xpath("//a[@href]")

        return [e.attrib['href'] for e in elements if e.attrib['href']]
