# https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker
FROM python:3.9-slim as dev

RUN apt-get update && \
    apt-get -y install curl build-essential && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py > get-poetry.py && \
    python get-poetry.py --version 1.1.6 && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -r /var/lib/apt/lists/* /usr/share/doc/* || true
ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR /usr/app

COPY src src
COPY tests tests
COPY mypy.ini .coveragerc pytest.ini pyproject.toml poetry.lock ./

RUN poetry install && \
    poetry export -f requirements.txt --without-hashes -o requirements.txt && \
    poetry build -f wheel && \
    poetry run pip install --upgrade pip && \
    poetry run pip wheel -w wheels -r requirements.txt && \
	mv dist/* wheels

EXPOSE 5000


FROM python:3.9-slim AS prod

WORKDIR /usr/app

COPY --from=dev /usr/app/wheels ./wheels/

RUN pip install --upgrade pip && \
    pip install wheels/* --no-deps --no-index

USER 1000

EXPOSE 5000

ENTRYPOINT [ "murkelhausen", "serve", "-h", "0.0.0.0" ]