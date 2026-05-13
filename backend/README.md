# Backend

FastAPI 后端骨架。

## 本地启动

```bash
uv sync --extra dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## 数据库迁移

```bash
uv run alembic upgrade head
```

创建新迁移：

```bash
uv run alembic revision --autogenerate -m "描述"
```

## 微信登录配置

后端使用 `.env` 配置文件。

配置文件：

- 示例模板：`backend/.env.example`
- 本地配置：`backend/.env`

`backend/.env` 示例：

```dotenv
SCHOOL_NOTIFY_DATABASE_URL=postgresql+psycopg://postgres:密码@主机:5432/school_notify
SCHOOL_NOTIFY_REDIS_URL=redis://主机:6379/0
SCHOOL_NOTIFY_REDIS_PASSWORD=redis密码
SCHOOL_NOTIFY_REDIS_KEY_PREFIX=school-notify
SCHOOL_NOTIFY_AUTH_SESSION_CACHE_TTL_SECONDS=7200
SCHOOL_NOTIFY_DEVICE_ONLINE_TTL_SECONDS=90
SCHOOL_NOTIFY_WECHAT_APP_ID=你的小程序 appid
SCHOOL_NOTIFY_WECHAT_APP_SECRET=你的小程序 secret
SCHOOL_NOTIFY_SESSION_SIGNING_SECRET=用于签名 session token 的随机字符串
SCHOOL_NOTIFY_ADMIN_USERNAME=admin
SCHOOL_NOTIFY_ADMIN_PASSWORD=replace_with_admin_password
SCHOOL_NOTIFY_ADMIN_DISPLAY_NAME=系统管理员
```

## 初始化管理员

执行：

```bash
uv run python bootstrap_admin.py
```

默认脚本会创建一个管理员账号；如账号已存在则不会重复创建。

后端会在 `POST /api/auth/login` 中使用微信 `code2Session` 接口换取 `openid`，并直接把 `openid` 作为当前阶段的 `user_id`。

同时，后端会使用 `SCHOOL_NOTIFY_SESSION_SIGNING_SECRET` 对返回的 `session_token` 做签名校验，避免仅靠明文前缀判断身份。

当前还额外维护服务端活跃 session：

- `POST /api/auth/login`：创建并登记 session
- `GET /api/auth/whoami`：要求 token 已登记且有效
- `POST /api/auth/logout`：撤销当前 session

当前阶段已落库的实体：

- `users`
- `auth_sessions`
- `devices`
- `device_bind_codes`
- `user_devices`（联合唯一约束 `user_id + device_id`）
- `notifications`
- `notification_deliveries`（联合唯一约束 `notification_id + device_id`）

Redis 当前用于以下场景：

**绑定码缓存**
- 生成绑定码时写入 Redis，并使用过期时间自动回收
- 用户提交绑定码时优先走 Redis 命中，再回退到数据库
- 绑定成功后会删除数据库绑定码，保证绑定码一次性消费

**会话缓存**
- 登录/创建会话时同步写入 Redis（默认 TTL 7200s）
- 鉴权命中缓存时自动续期（滑动 TTL）
- DB 回查命中后也会回写缓存
- 注销时同时清除 Redis 缓存

**设备在线状态**
- 设备注册/心跳时在 Redis 设置在线标记（默认 TTL 90s，可通过 `DEVICE_ONLINE_TTL_SECONDS` 配置）
- `last_seen` 时间戳同步写入 Redis（TTL = 在线 TTL × 2），自动过期清理
- 查询设备列表时优先读取 Redis 在线状态
- 心跳停止后自动过期为离线

当前仅 `delivery_receipts` 的内存镜像用于兼容现有测试断言，真实投递状态以 `notification_deliveries` 为准。

## 测试

```bash
uv run pytest
```
