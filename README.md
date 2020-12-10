# The parser of related URLs in HTML page

![Project language][badge_language]
![Docker][badge_docker]
[![Build Status][badge_build]][link_build]
[![Do something awesome][badge_use_template]][use_this_repo_template]

### Usage

```
usage: index.py [-h] [-d DEPTH] [-n LIMIT] [--allow-external-urls]
[--log-level {debug,info,warning,error}]
[--requests-batch-limit BOUNDED_SEMAPHORE]
{get,load} url

positional arguments:
{get,load} : 'get' - show from db, 'load' - request and parse
url

optional arguments:
-h, --help
show this help message and exit

-d DEPTH, --depth DEPTH
Limit depth to parse (default=1)

-n LIMIT, --limit LIMIT
Limit to show urls (default=0)

--allow-external-urls
Allow links to other domains (default=False)

--log-level {debug,info,warning,error}
Level of logging info (default=INFO)

--requests-batch-limit BOUNDED_SEMAPHORE
Increase it when you can do more requests in one batch
or decrease in case you get HTTP-429 (TooManyRequests)
error (default=6)
```

### Functions
- `load` - request to URL, parse, request to related URLs depends on arguments, store to DB
- `get` - select from DB URLs that are in HTML of input URL

### How to use
- `docker-compose pull`
- `docker-compose build`
- `docker-compose up -d db`
- `docker-compose run app python index.py *args`

#### Example of run
- `docker-compose run app python index.py load https://www.lookout.net --depth 2 --log-level=info`
- `docker-compose run app python index.py get https://www.lookout.net -n 0`

### Pay attention
- Argument `--depth` is limited only depends on your RAM
- If you got HTTP status code 429 (Too many requests) then wait some time and try with decreased argument `--requests-batch-limit` to 1 or 2 (default = 6)
- If the parsed domain do not limit requests, then you may improve speed of parsing by increase argument `--requests-batch-limit` (I do not recommend > 100) 

### Requirements
- `Docker`; `docker-compose`
- **or** locally installed and configured `python3.6+`, `python3.6+-dev`, `postgres`

### Todos
- Implement all TODO-s in code
- Create Logger instance in each file
- Add support `--depth` in `get` method
- Add validation of URLs (validator already in code but unused)

[badge_build]:https://github.com/avtocod/python-developer-test-task/workflows/CI/badge.svg
[badge_language]:https://img.shields.io/badge/python-3-yellow?longCache=true
[badge_docker]:https://img.shields.io/badge/docker-enable-blue?longCache=true
[badge_use_template]:https://img.shields.io/badge/start-this_template_using-success.svg?longCache=true
[link_build]:https://github.com/avtocod/python-developer-test-task/actions
[link_create_issue]:https://github.com/avtocod/python-developer-test-task/issues/new
[use_this_repo_template]:https://github.com/avtocod/python-developer-test-task/generate
