FROM python:3.10-slim-buster

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN pip install poetry

COPY . /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT [ "sh", "entrypoint.sh" ]