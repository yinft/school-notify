# Docker Compose Deployment

## Overview

This deployment starts the backend, PostgreSQL, and Redis on a single server with `docker compose`.

Only the backend is exposed publicly on port `8000`.
PostgreSQL and Redis are published on `127.0.0.1` only for server-local access and SSH tunnels.

## Prerequisites

1. Install Docker and Docker Compose plugin on the server.
2. Open `8000/tcp` in the server firewall or security group.
3. Clone this repository to the server.

## Prepare Environment Variables

1. Copy the template file:

```bash
mkdir -p deploy
cp deploy/backend.env.example deploy/backend.env
```

2. Edit `deploy/backend.env` and replace every placeholder value.

Important values:

- `POSTGRES_PASSWORD`
- `POSTGRES_TIMEZONE`
- `BACKEND_TIMEZONE`
- `SCHOOL_NOTIFY_DATABASE_URL`
- `SCHOOL_NOTIFY_REDIS_PASSWORD`
- `SCHOOL_NOTIFY_SESSION_SIGNING_SECRET`
- `SCHOOL_NOTIFY_WECHAT_APP_ID`
- `SCHOOL_NOTIFY_WECHAT_APP_SECRET`
- `SCHOOL_NOTIFY_ADMIN_USERNAME`
- `SCHOOL_NOTIFY_ADMIN_PASSWORD`
- `SCHOOL_NOTIFY_ADMIN_DISPLAY_NAME`

`SCHOOL_NOTIFY_DATABASE_URL` must keep `postgres` as the database host:

```dotenv
SCHOOL_NOTIFY_DATABASE_URL=postgresql+psycopg://postgres:your_password@postgres:5432/school_notify
```

`SCHOOL_NOTIFY_REDIS_URL` must keep `redis` as the host for the backend container, and Redis now requires a password:

```dotenv
SCHOOL_NOTIFY_REDIS_URL=redis://redis:6379/0
SCHOOL_NOTIFY_REDIS_PASSWORD=replace_with_strong_redis_password
```

All `docker compose` commands below must load that env file explicitly:

```bash
docker compose --env-file deploy/backend.env up -d --build
```

PostgreSQL defaults to `Asia/Shanghai` in this compose file. You can change it by editing:

```dotenv
POSTGRES_TIMEZONE=Asia/Shanghai
```

Backend container logs default to Beijing time through the container timezone setting:

```dotenv
BACKEND_TIMEZONE=CST-8
```

## Start Services

Build and start the stack:

```bash
docker compose --env-file deploy/backend.env up -d --build
```

Check container status:

```bash
docker compose --env-file deploy/backend.env ps
```

Check backend logs:

```bash
docker compose --env-file deploy/backend.env logs backend
```

## Verify Deployment

Run a local health check on the server:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","service":"school-notify-backend"}
```

## Bootstrap Admin Account

After the backend container is up, create the initial admin account inside the backend container:

```bash
docker compose --env-file deploy/backend.env exec backend uv run python bootstrap_admin.py
```

This script reads these environment variables:

```dotenv
SCHOOL_NOTIFY_ADMIN_USERNAME=admin
SCHOOL_NOTIFY_ADMIN_PASSWORD=replace_with_admin_password
SCHOOL_NOTIFY_ADMIN_DISPLAY_NAME=系统管理员
```

The script is idempotent for the same username. If the admin already exists, it keeps the existing account.

## Admin And Website Frontend Environment

Recommended frontend environment variables:

```dotenv
VITE_API_BASE_URL=https://your-api-domain
NUXT_PUBLIC_BACKEND_BASE_URL=https://your-api-domain
```

- `admin` uses `VITE_API_BASE_URL` to call `/api/admin/*`
- `website` uses `NUXT_PUBLIC_BACKEND_BASE_URL` to call `/api/public/versions*`
- If the website variable is empty, the homepage falls back to static version content

You can also verify from another machine:

```bash
curl http://YOUR_SERVER_IP:8000/health
```

## Access PostgreSQL And Redis Over SSH

This compose setup publishes PostgreSQL and Redis only on the server loopback interface:

- PostgreSQL: `127.0.0.1:5432`
- Redis: `127.0.0.1:6379`

They are not directly reachable from the public network. To connect from your local machine, open SSH tunnels:

```bash
ssh -L 5432:127.0.0.1:5432 -L 6379:127.0.0.1:6379 user@YOUR_SERVER_IP
```

Then connect locally:

```bash
psql postgresql://postgres:YOUR_POSTGRES_PASSWORD@127.0.0.1:5432/school_notify
redis-cli -a YOUR_REDIS_PASSWORD -h 127.0.0.1 -p 6379
```

## Stop Services

Stop containers without removing data:

```bash
docker compose --env-file deploy/backend.env down
```

## Rebuild After Code Changes

Pull the latest code and rebuild:

```bash
git pull
docker compose --env-file deploy/backend.env up -d --build
```

## Notes

- PostgreSQL data is stored in the `postgres_data` volume.
- Redis data is stored in the `redis_data` volume.
- PostgreSQL and Redis are bound to `127.0.0.1` and are not exposed to the public network.
- Redis requires `SCHOOL_NOTIFY_REDIS_PASSWORD` for both the backend and operator access.
- PostgreSQL runs with timezone `Asia/Shanghai` by default.
- The backend runs `alembic upgrade head` before starting Uvicorn.
