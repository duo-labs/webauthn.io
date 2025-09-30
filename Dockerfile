# Tweak the base image by installing pipenv
FROM python:3.10-slim AS base
RUN pip install pipenv

# Begin our actual build
FROM base AS base1
# collectstatic needs the secret key to be set. We store that in this environment variable.
# Set this value in this project's .env file
ARG DJANGO_SECRET_KEY

RUN mkdir -p /usr/src/app

COPY ./_app /usr/src/app
COPY Pipfile /usr/src/app/
COPY Pipfile.lock /usr/src/app/

WORKDIR /usr/src/app

# Install Python dependencies
RUN pipenv install --system --deploy

# Collect static files
RUN python manage.py collectstatic --no-input
