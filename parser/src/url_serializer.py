from parser import URLRepresentation


class URLSerializer(object):

    def __init__(self, url: str, title: str, html: str):
        self.url = URLRepresentation.prepare_url(url)
        self.title = URLSerializer.prepare_title(title)
        self.html = html

    def __repr__(self):
        return {
            "name": self.url,
            "title": self.title,
            "html": self.html
        }

    @staticmethod
    def prepare_title(title: str) -> str:
        title_ = title.strip()

        return title_
