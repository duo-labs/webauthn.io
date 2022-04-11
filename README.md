# Docker'd Django
### Django, Postgres, and Redis, all in Docker

This is a boilerplate repo intended for quickly starting a new **Django** project with **PostgreSQL** and **Redis** support, all running within Docker containers. A **Nginx** service is also defined to enable immediate access to the site over port 80, with production hosting over HTTPS made possible via **Cloudflare Tunnel**.

- [Prerequisites](#prerequisites)
- [Getting started](#getting-started)
- [Components](#components)
- [Production Hosting](#production-hosting)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker
- Pipenv
  - Make sure Python3 is available
  - Enables `pipenv install` to set up libraries locally for the editor to crawl. The Django container also uses Pipenv to install dependencies to encourage use of this new Python package management tool.

## Getting started

1. Clone this repo
2. Delete the **.git** folder
    - `rm -rf .git/`
3. Create a new git repo
    - `git init`
    - `git add .`
    - `git commit -m "Initial Commit"`
4. Install Python dependencies in a Python3 virtual environment
    - `pipenv install --three`
5. Create a new Django project
    - `pipenv run django-admin startproject appname _app/`
6. Make the following changes to your Django project's **settings.py**:

```py
# appname/settings.py
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', False) == 'true'

ALLOWED_HOSTS = [
    'localhost',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_USER'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    }
}

STATIC_ROOT = 'static'

# Redis cache support
# https://docs.djangoproject.com/en/4.0/topics/cache/#redis-1

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

7. Update the **.env** file to specify values for the environment variables defined within
8. Do a global search of all files here for "appname" and replace it with the actual name of your app
9. Start Django for development at http://localhost:8000
    - `docker compose up`

## Components

### Dockerfile

Builds the Django container. The container is built from a standard **python** Docker image and will run Django's `colletstatic` when being built.

### docker-compose.yml

Tasked with spinning up three containers: the above container for **Django**, one for **PostgreSQL**, and one for **Redis**.

By default an **Nginx** container is also created to reverse-proxy requests to Django and serve static files. In this configuration, the Django server will be available on port 80 during production.

If the Nginx container is removed, Docker can be accessed directly on port 8000. Static files can then be served from the **static_files_volume** Docker volume.

### docker-compose.override.yml

Loads automatically when running a standard `docker-compose up`. These values are intended for development purposes as they tweak the container configurations in the following way:

- Make the Postgres container accessible externally on port 5432
- Make the site available through Nginx at http://localhost:8000
- Start gunicorn to reload when it detects a file change
- Set an environmental flag telling Django that it is running in debug mode

### Pipfile/Pipfile.lock

Includes Python packages needed to make Django, Postgre, and Redis work together.

### .env

Contains environment variables for the containers. Several variables are included for configuring Postgres and Django secrets.

### .dockerignore

Defines files that Docker should _never_ include when building the Django image.

### .editorconfig

Defines some common settings to help ensure consistency of styling across files.

### .flake8

Configures the **flake8** Python linter. Includes a few common settings to my personal preferences.

### .vscode/settings.json

Helps configure the Python plugin to lint with flake8. A placeholder Python interpreter setting is left in to simplify pointing to the local virtual environment created with Pipenv.

### _app/gunicorn.cfg.py

Defines settings for gunicorn, including a port binding, workers, and a gunicorn-specific error log.

### _ngingx/nginx.conf
### _nginx/templates/default.conf.conf

Establishes a reverse-proxy to Django, and serves Django static files. The default template leverages the nginx Docker image's ability to reference environment variables via envsubst; this is how the `PROD_HOST_NAME` environment variable is referenced for production access.

### start-dev.sh

An executable script for starting the server in development mode.

### start-prod.sh

An executable script for starting the server in production mode.

### update-prod-django.sh

An executable script for rebuilding and restarting production Django whenever there's a change. This script also restarts Nginx to ensure no traffic hits the server while the update occurs.

## Production Hosting

### Cloudflare Tunnel

The `cloudflaretunnel` service in **docker-compose.yml** can be used to set up HTTPS access to Django via [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/). To get started, follow these steps:

1. Log into the [Cloudflare Zero Trust dashboard](https://dash.teams.cloudflare.com/)
2. Click **Access > Tunnels**
3. Click **Create a tunnel**
4. Specify a **Tunnel name**
5. Click **Docker** on the **Install connector** step
6. Save the value of the `--token` flag in the page's `docker` command to this project's **.env** file as the `CLOUDFLARE_TUNNEL_TOKEN` environment variable
7. Run **start-prod.sh** to start the tunnel and display an entry under **Connectors**
8. Click **Next**
9. Set up a **Public hostname**
10. For the **Service** select "**HTTP**" and then enter "**nginx**"
11. Click **Save &lt;tunnel name&gt; tunnel** to complete setup
12. Set the `PROD_HOST_NAME` variable in the **.env** file to the tunnel's configured **Public hostname**

You will also need to make the following change to Django's **_app/appname/settings.py** to add `PROD_HOST_NAME` as an allowed hostname:

```py
ALLOWED_HOSTS = [
    os.getenv("PROD_HOST_NAME", ""),
    "localhost",
]
```

When these steps are complete, running **start-prod.sh** should make Django available on the public internet at `https://$PROD_HOST_NAME`. No firewall ports need to be opened on the production host, and in fact you may wish to set up the firewall to block all incoming traffic for good measure.

## Troubleshooting

### The Django container reports "exited with code 3"

You probably forgot to replace the string "appname" with the actual name you passed to `django-admin startproject`. Check **_app/gunicorn_appname.log** to see if Gunicorn is erroring out with something like this:

```
ModuleNotFoundError: No module named 'appname'
```
