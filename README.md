# webauthn.io

Duo's introduction to the wonderful world of WebAuthn. Powered by [py_webauthn](https://github.com/duo-labs/py_webauthn).

## Prerequisites

- Docker
- uv (See https://docs.astral.sh/uv/getting-started/installation/)
  - Run `uv sync` locally to install dependencies and give the editor something to crawl

## Environmental Variable

- `DJANGO_SECRET_KEY`: A sufficiently random string
- `PROD_HOST_NAME`: The domain name the site will be hosted at
- `PROD_CSRF_ORIGIN`: The domain name plus protocol from which requests to the backend should occur (e.g. `https://webauthn.io`)
- `RP_ID`: The Relying Party ID, typically the same as `PROD_HOST_NAME`
- `RP_NAME`: A representation of the site's name to be shown to users
- `RP_EXPECTED_ORIGIN`: The domain name plus protocol at which WebAuthn will be invoked (e.g. `https://webauthn.io`)

## Development

Run the following command to get started:

```sh
./start-dev.sh
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
./start-prod.sh
```

The site will be available for viewing at https://{PROD_HOST_NAME}. The included [Caddy server](https://caddyserver.com/) (as the `caddy` service in **docker-compose.yml**) will handle SSL certificate management.

## Updating Production

Run the following commands to rebuild and restart the `django` service with any new updates:

```sh
$> git pull
$> ./update-prod-django.sh
```

The `django` and `caddy` services will be temporarily stopped during the build, and will restart once the `django` has been rebuilt.

## Testing

Run the following command to test everything in the `homepage.tests` module:

```sh
./run-tests.sh
```

## A Note about WebAuthn Privacy Considerations

This site is **not** intended to represent WebAuthn best practices. Its use of WebAuthn is optimized to offer a test bed for the many permutations of possible WebAuthn API calls.

As a result the codebase does not meaningfully try to offer solutions to any of the [Relying Party-specific privacy considerations](https://www.w3.org/TR/webauthn/#sctn-privacy-considerations-rp) as detailed in the spec, like username enumeration or personal information leakage via user ID.

Please keep this in mind as you dive deeper into the internals of this project. You can consult the spec at the link above for ideas on how to address these problems for your Relying Party implementation.
