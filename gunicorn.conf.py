"""Gunicorn configuration file.

:ref: https://github.com/tiangolo/meinheld-gunicorn-docker/blob/master/docker-images/gunicorn_conf.py  # noqa

"""

import multiprocessing
import os

workers_per_core_str = os.getenv("GUNICORN_WORKERS_PER_CORE", "1")
web_concurrency_str = os.getenv("GUNICORN_WEB_CONCURRENCY", None)
host = os.getenv("GUNICORN_HOST", "0.0.0.0")
port = os.getenv("GUNICORN_PORT", "80")
bind_env = os.getenv("GUNICORN_BIND", None)
use_loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores

if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = int(default_web_concurrency)

#: Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
keepalive = 120
errorlog = "-"

#: For debugging and testing
log_data = {
    "bind": bind,
    "host": host,
    "loglevel": loglevel,
    "port": port,
    "workers": workers,
    #: Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
}
