# Tweak the base image by installing uv
FROM python:3.10-slim AS base

# Install uv (https://docs.astral.sh/uv/)
COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /uvx /bin/

# Begin our actual build
FROM base AS base1
# collectstatic needs the secret key to be set. We store that in this environment variable.
# Set this value in this project's .env file
ARG DJANGO_SECRET_KEY

RUN mkdir -p /usr/src/app

COPY ./_app /usr/src/app
COPY pyproject.toml uv.lock /usr/src/app/

WORKDIR /usr/src/app

# Install Python dependencies
RUN uv sync --locked

# Collect static files
RUN uv run python manage.py collectstatic --no-input
