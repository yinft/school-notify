# Docker Compose Deployment

## Overview

This deployment starts the backend, PostgreSQL, and Redis on a single server with `docker compose`.

Only the backend is exposed publicly on port `8000`.

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
- `SCHOOL_NOTIFY_SESSION_SIGNING_SECRET`
- `SCHOOL_NOTIFY_WECHAT_APP_ID`
- `SCHOOL_NOTIFY_WECHAT_APP_SECRET`

`SCHOOL_NOTIFY_DATABASE_URL` must keep `postgres` as the database host:

```dotenv
SCHOOL_NOTIFY_DATABASE_URL=postgresql+psycopg://postgres:your_password@postgres:5432/school_notify
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

You can also verify from another machine:

```bash
curl http://YOUR_SERVER_IP:8000/health
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
- PostgreSQL and Redis are not exposed to the public network.
- PostgreSQL runs with timezone `Asia/Shanghai` by default.
- The backend runs `alembic upgrade head` before starting Uvicorn.
