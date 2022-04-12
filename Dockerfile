FROM python:3-slim-buster
LABEL Description="Parse hyperlinks" Vendor="mail@s-savelyev.ru"

RUN groupadd --system parser && useradd --no-log-init --shell /bin/false --system --gid parser parser

ENV TZ='Europe/Moscow'
ENV APP_DIR=/app

WORKDIR ${APP_DIR}

COPY ./requirements.txt ${APP_DIR}/requirements.txt
COPY ./requirements-dev.txt ${APP_DIR}/requirements-dev.txt

RUN pip install --no-cache-dir -r ${APP_DIR}/requirements.txt -r ${APP_DIR}/requirements-dev.txt

COPY sitemapgen ./parser
COPY ./tests ./tests

USER parser

CMD ["python", "-m", "parser"]
