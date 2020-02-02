FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

COPY poetry.lock pyproject.toml /app/

WORKDIR /app

# Check docker-compose for more info about the ARG and ENV variables
ARG PIP_NO_CACHE_DIR
ARG POETRY_VIRTUALENVS_CREATE

ENV POETRY_VIRTUALENVS_CREATE ${POETRY_VIRTUALENVS_CREATE}

# Configure apk and install packages
RUN apk --no-cache add --virtual build-dependencies build-base jpeg-dev zlib-dev libffi-dev openssl-dev \
    && apk --no-cache add --virtual runtime-dependencies jpeg zlib \
    # Install poetry for better dependency management
    && pip install poetry \
    && poetry install --no-dev --no-root \
    # Clean up installed packages
    && apk del build-dependencies
