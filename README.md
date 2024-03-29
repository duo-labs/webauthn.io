# webauthn.io

Duo's introduction to the wonderful world of WebAuthn. Powered by [py_webauthn](https://github.com/duo-labs/py_webauthn).

## Prerequisites

- Docker
- Pipenv
  - Make sure Python3 is available
  - Enables `pipenv install` to set up libraries locally for the editor to crawl. The Django container also uses Pipenv to install dependencies to encourage use of this new Python package management tool.

## Environmental Variable

- `DJANGO_SECRET_KEY`: A sufficiently random string
- `PROD_HOST_NAME`: The domain name the site will be hosted at
- `RP_ID`: The Relying Party ID, typically the same as `PROD_HOST_NAME`
- `RP_NAME`: A representation of the site's name to be shown to users
- `RP_EXPECTED_ORIGIN`: The domain name plus protocol at which WebAuthn will be invoked (e.g. `https://webauthn.io`)

## Development

Run the following command to get started:

```sh
$> ./start-dev.sh
```

The site will be available at http://localhost/

### CSS

CSS leans on browsers and their [native CSS nesting support](https://blog.logrocket.com/native-css-nesting/), which allows for nicer CSS authoring without pre-processors. Unfortunately for now this means the following command will need to be run after making any changes to CSS to ensure that the changes are served by Caddy on subsequent reloads:

```sh
docker compose run django ./manage.py collectstatic --no-input
```

## Production

Run the following command to start up the website with production-ready settings:

```sh
$> ./start-prod.sh
```

The site will be available for viewing at https://{PROD_HOST_NAME}. The included [Caddy server](https://caddyserver.com/) (as the `caddy` service in **docker-compose.yml**) will handle SSL certificate management.

## Updating Production

Run the following commands to rebuild and restart the `django` service with any new updates:

```sh
$> git pull
$> ./update-prod-django.sh
```

The `django` and `caddy` services will be temporarily stopped during the build, and will restart once the `django` has been rebuilt.
