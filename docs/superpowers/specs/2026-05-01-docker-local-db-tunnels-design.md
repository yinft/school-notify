# Docker Local-Only Database Access Design

## Goal

Keep PostgreSQL and Redis reachable from the server host for maintenance and SSH tunneling, but prevent direct public network access.

## Decisions

- PostgreSQL will publish `5432` only on `127.0.0.1`.
- Redis will publish `6379` only on `127.0.0.1`.
- Backend-to-database traffic will stay on the Docker Compose internal network using the existing service names `postgres` and `redis`.
- Redis will require a password via `SCHOOL_NOTIFY_REDIS_PASSWORD`.
- Deployment docs and env examples will show the local-only access model and SSH tunnel usage.

## Rationale

Binding published ports to `127.0.0.1` allows operators to reach PostgreSQL and Redis from the server itself or through SSH local port forwarding, while avoiding any direct public exposure from Docker port publishing.

Redis should not rely on network isolation alone. Requiring a password reduces the risk of accidental local misuse and protects the service if the binding is widened later by mistake.

## Scope

- Update `docker-compose.yml`.
- Update deployment env examples.
- Update Docker Compose deployment documentation.

## Out Of Scope

- Credential rotation.
- Firewall automation.
- TLS for PostgreSQL or Redis.
