FROM python:3.10.2-alpine
LABEL maintainer="A. J. Wray <ajw@ajw.sl>"

RUN apk add build-base \
    chromium-chromedriver \
    clang \
    curl \
    gcc \
    gdal \
    gdal-dev \
    git \
    libffi-dev \
    lld \
    musl-dev \
    openssl-dev \
    patchelf \
    proj \
    proj-dev \
    proj-util \
    python3-dev \
    wget

RUN curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

#: Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python
ENV PYTHONPATH=/var/www
ENV PATH=$PATH:/root/.cargo/bin:/opt/poetry/bin

WORKDIR /var/www
COPY poetry.lock pyproject.toml /var/www/
RUN poetry config virtualenvs.create true && \
    poetry install --no-root

#: Copy .env
COPY gunicorn.conf.py /var/www/gunicorn.conf.py
COPY leonify.py /var/www/leonify.py

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn.conf.py", "leonify:application"]
