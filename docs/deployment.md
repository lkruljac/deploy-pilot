# Deployment

## One-time: Watchtower

Installed once on the NAS and shared by every service. See
[`pipeline/watchtower.compose.yaml`](../pipeline/watchtower.compose.yaml).

It only acts on containers labelled `com.centurylinklabs.watchtower.enable=true`,
so existing stacks are never touched.

## One-time per service

1. Copy [`pipeline/compose.nas.yaml`](../pipeline/compose.nas.yaml) to
   `/volume1/docker/deploy-pilot/compose.yaml` on the NAS.
2. Create the project in DSM Container Manager so it survives a reboot.
3. Add two DSM reverse proxy entries:

   | Source | Destination | Access |
   |--------|-------------|--------|
   | `https://deploy-pilot.lukak.dev:443` | `http://localhost:8150` | per service |
   | `https://deploy-pilot-develop.lukak.dev:443` | `http://localhost:9150` | LAN only |

Pi-hole resolves `*.lukak.dev` to the NAS by wildcard, so no DNS entry is needed
per service.

## Port convention

Production uses the `81x0` band, develop mirrors it at `91x0`.

| Service | Production | Develop |
|---------|-----------|---------|
| landing | 8110 | — |
| kil | 8120 | 9120 |
| topology | 8130 | 9130 |
| godisnji | 8140 | 9140 |
| deploy-pilot | 8150 | 9150 |

Containers bind to `127.0.0.1`, never `0.0.0.0`. This keeps the DSM reverse proxy
the only route in, so its access control profile cannot be bypassed by anything
on the LAN addressing the port directly.

## Routine deploys

Push to `develop` or `master`. Watchtower picks up the new image within its poll
interval, currently five minutes. Confirm by reloading the page and checking the
commit shown against the latest commit on the branch.

## Private images

Public images need no credentials. When a service's package is made private, run
on the NAS:

```bash
docker login ghcr.io -u lkruljac
```

and paste a classic PAT scoped to `read:packages` only. Watchtower reads the
resulting `~/.docker/config.json`. One token covers every private image.

## Rolling back

Every build also publishes `:sha-<short>`. Pin the compose file to a known-good
SHA tag and redeploy:

```yaml
image: ghcr.io/lkruljac/deploy-pilot:sha-abc1234
```

Watchtower will not move a pinned tag, so the rollback holds until the tag is
changed back.
