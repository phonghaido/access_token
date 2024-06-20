FROM python:3.12-alpine as builder

ENV PYTHONUNBUFFERED=1 \
	POETRY_NO_INTERACTION=1 \
	POETRY_VIRTUALENVS_IN_PROJECT=1 \
	POETRY_VIRTUALENVS_CREATE=1 \
	POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN apk add --update --no-cache --virtual .build-dependencies make build-base linux-headers gcc python3-dev

RUN pip install poetry==1.8.2

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
RUN apk del .build-dependencies

FROM python:3.12-alpine
ENV VIRTUAL_ENV=/app/.venv \
	PATH="/app/.venv/bin:$PATH"
WORKDIR /app

RUN apk add curl

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY /app /app

EXPOSE 8000
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]