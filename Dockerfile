FROM python:3.8-alpine AS build

ENV PYTHONUNBUFFERED 1

WORKDIR /tmp

COPY poetry.lock pyproject.toml /tmp/

# Configure poetry to generate requirements.txt from poetry.lock
RUN apk --no-cache add --virtual build-dependencies build-base libffi-dev openssl-dev \
    && pip --no-cache-dir install poetry \
    && poetry export -f requirements.txt > requirements.txt \
    && apk del build-dependencies


FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY --from=build /tmp/requirements.txt /tmp/requirements.txt

# Configure apk and install packages
RUN apk --no-cache add --virtual build-dependencies build-base jpeg-dev zlib-dev \
    && apk --no-cache add --virtual runtime-dependencies jpeg zlib \
    # Install dependencies
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    # Clean up installed packages
    && apk del build-dependencies
