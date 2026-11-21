# deploy-pilot

A minimal service whose only job is to prove a CI/CD chain works end to end. It serves a page showing the branch, commit and build time baked into the running image, so a successful deploy is visible at a glance rather than inferred from logs.

It is the reference implementation for deploying self-hosted services onto a Synology NAS without exposing anything new to the internet.

## How it works

```
push to develop/master
        │
        ▼
GitHub Actions  ──  builds the image on GitHub's runners
        │
        ▼
    ghcr.io     ──  tagged :latest (master) / :develop / :sha-<short>
        │
        ▼
  Watchtower    ──  polls from inside the LAN, pulls, restarts
        │
        ▼
   DSM nginx    ──  terminates TLS with the *.lukak.dev wildcard cert
        │
        ▼
    Traefik     ──  routes by Host label, applies LAN-only access control
        │
        ▼
  container     ──  no host port, reached over the shared `edge` network
```

Three properties this design is built around:

- **Nothing new is exposed.** Watchtower polls outbound, so there is no webhook endpoint, no port forward and no inbound path to the NAS.
- **No build load on the NAS.** Images are built on GitHub's hardware; the NAS only pulls and runs.
- **No registry credentials to manage.** Actions pushes to GHCR using the automatic `GITHUB_TOKEN`. A read-only token is needed on the NAS only once images become private.
- **No ports to allocate.** Services publish nothing to the host. Routing and access control are compose labels, so adding a service is a config change rather than a port-assignment decision.

A self-hosted runner is deliberately *not* used for public repositories: a pull request from a fork can execute arbitrary code on it, and a deploy runner needs Docker socket access. The pull-based design avoids that entirely.

## Layout

```
.
├── .github/workflows/   CI — must live here, GitHub requires it
├── src/                 application code
├── pipeline/            deployment manifests for the NAS
├── docs/                deployment and local development guides
├── Dockerfile
└── compose.yaml         local development only
```

## Quick start

```bash
docker compose up --build
```

Then open <http://localhost:8080>.

## Endpoints

| Path | Purpose |
|------|---------|
| `/` | build info page |
| `/version` | same data as JSON |
| `/healthz` | liveness probe |

## Environments

| Branch | Image tag | URL |
|--------|-----------|-----|
| `master` | `:latest` | `deploy-pilot.lukak.dev` |
| `develop` | `:develop` | `deploy-pilot-develop.lukak.dev` |

Develop is restricted to the LAN by a DSM access control profile. Production exposure is decided per service.

## Documentation

- [Local development](docs/local-development.md)
- [Deployment](docs/deployment.md)
