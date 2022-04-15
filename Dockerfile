FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev

COPY main.py ./
RUN poetry install --no-dev

CMD poetry run python -m main
