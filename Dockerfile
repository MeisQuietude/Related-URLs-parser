FROM ubuntu:20.10

COPY ./requirements.txt ./requirements-dev.txt ./package_list.txt /app/

WORKDIR /app

USER root

CMD ["bash"]

RUN set -x; \
    apt-get update \
    && apt-get install $(cat package_list.txt) -y --no-install-recommends \
    && apt-get clean

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10

RUN python -m pip install -r requirements.txt -r requirements-dev.txt

RUN groupadd -r parse_user -g 901 \
    && useradd -u 901 -r -g parse_user --shell=/bin/bash parse_user

COPY . .

USER parse_user

CMD ["python"]
