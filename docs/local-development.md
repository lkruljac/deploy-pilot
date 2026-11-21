# Local development

## Run with Docker

```bash
docker compose up --build
```

<http://localhost:8080>

Build metadata is set to `local` so a locally built container is never mistaken for a deployed one.

## Run without Docker

```bash
python src/app.py
```

Honours `PORT`, `ENVIRONMENT`, `GIT_SHA`, `GIT_BRANCH` and `BUILD_TIME`. All are optional.

The application is deliberately dependency-free — it uses only the Python standard library, which keeps image builds near-instant and the CI minute cost negligible.

## Branching

| Branch | Effect on push |
|--------|----------------|
| `develop` | builds `:develop`, auto-deploys to the develop URL |
| `master` | builds `:latest`, auto-deploys to production |
| anything else | no build |

Work on a feature branch, merge to `develop` to see it live on the LAN, merge to `master` to release.

## Before committing

The image is public, so anything baked into it is public. Secrets belong in `.env` on the NAS, never in the repository or the image. `.gitignore` already excludes `.env` files.
