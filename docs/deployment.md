# Deployment

## Request path

```
https://<service>.lukak.dev
        │
        ▼
DSM nginx :443         terminates TLS with the *.lukak.dev wildcard cert
        │              one entry per hostname, all pointing at :8081
        ▼
Traefik :8081          routes by Host label, applies access control
        │
        ▼
container :8080        no host port, reached over the `edge` network
```

## One-time NAS setup

```bash
docker network create edge
```

Then deploy Traefik from [`pipeline/traefik.compose.yaml`](../pipeline/traefik.compose.yaml)
and Watchtower from [`pipeline/watchtower.compose.yaml`](../pipeline/watchtower.compose.yaml).

Watchtower only acts on containers labelled
`com.centurylinklabs.watchtower.enable=true`, so pre-existing stacks are never
touched.

## Per service

1. Copy [`pipeline/compose.nas.yaml`](../pipeline/compose.nas.yaml) to
   `/volume1/docker/<service>/compose.yaml`, adjusting the hostnames in the
   router rules. There are no ports to allocate.
2. `docker compose up -d`
3. Add two DSM reverse proxy entries, **both pointing at `localhost:8081`**:

   | Source | Destination |
   |--------|-------------|
   | `https://<service>.lukak.dev:443` | `http://localhost:8081` |
   | `https://<service>-develop.lukak.dev:443` | `http://localhost:8081` |

4. Control Panel → Security → Certificate → **Settings**: set both new services
   to the `lukak.dev` certificate. New entries default to the DDNS certificate,
   which does not cover `lukak.dev` and produces
   `ERR_CERT_COMMON_NAME_INVALID`. Because `.dev` is an HSTS-preloaded TLD,
   browsers offer no click-through for this — the mapping is mandatory, not
   cosmetic.

Pi-hole resolves `*.lukak.dev` to the NAS by wildcard, so no DNS entry is
needed per service.

### Two DSM quirks that waste time

- The source **port field shows `443` as a placeholder, not a value**. Leaving
  it untouched fails validation with "The port number should be from 1 to
  65535". Type it explicitly.
- DSM rejects `*.lukak.dev` as a source hostname with "Invalid domain name", so
  a single wildcard entry covering every service is not possible. One entry per
  hostname is the minimum, which is why they all share one destination port.

## Access control

Public and LAN-only are decided by a Traefik label, not by DSM:

```yaml
- traefik.http.routers.<name>.middlewares=lanonly@docker
```

Omit it for public, include it for LAN-only. Develop should always include it.

Verify with:

```bash
curl -o /dev/null -w '%{http_code}\n' -H 'Host: <svc>-develop.lukak.dev' \
     -H 'X-Forwarded-For: 8.8.8.8' http://127.0.0.1:8081/   # expect 403
curl -o /dev/null -w '%{http_code}\n' -H 'Host: <svc>-develop.lukak.dev' \
     -H 'X-Forwarded-For: 192.168.0.99' http://127.0.0.1:8081/   # expect 200
```

## Routine deploys

Push to `develop` or `master`. Watchtower pulls the new image within its poll
interval, currently five minutes, and restarts the container.

Watchtower reacts to **image** changes only. It clones the existing container's
configuration rather than re-reading `compose.yaml`, so edits to the compose
file require `docker compose up -d` by hand.

## Rolling back

Every build also publishes `:sha-<short>`. Pin the compose file to a known-good
SHA tag and redeploy:

```yaml
image: ghcr.io/lkruljac/deploy-pilot:sha-abc1234
```

Watchtower will not move a pinned tag, so the rollback holds.

## Private images

Public images need no credentials. When a package is made private, run on the
NAS:

```bash
docker login ghcr.io -u lkruljac
```

and paste a classic PAT scoped to `read:packages`. Mount the resulting
`~/.docker/config.json` into Watchtower. One token covers every private image.
