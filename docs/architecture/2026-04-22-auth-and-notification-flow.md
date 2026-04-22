# Auth And Notification Flow

## 1. 微信登录时序图

```mermaid
sequenceDiagram
    participant MiniApp as 微信小程序
    participant Backend as FastAPI 后端
    participant WeChat as 微信 code2Session

    MiniApp->>WeChat: wx.login()
    WeChat-->>MiniApp: code
    MiniApp->>Backend: POST /api/auth/login { code }
    Backend->>WeChat: code2Session(appid, secret, js_code)
    WeChat-->>Backend: openid + session_key
    Backend-->>MiniApp: user_id=openid + session_token
    MiniApp->>MiniApp: 本地保存 authSession
```

## 2. 业务访问流程

```mermaid
flowchart TD
    A[页面 onShow] --> B{本地有登录态?}
    B -- 否 --> C[调用 app.ensureLogin]
    C --> D[wx.login + /api/auth/login]
    D --> E{登录成功?}
    E -- 否 --> F[展示统一登录态界面]
    E -- 是 --> G[保存 currentUserId 和 sessionToken]
    B -- 是 --> G
    G --> H[request 自动带 Bearer Token]
    H --> I[后端解析 session token]
    I --> J{token 已登记且 user_id 一致?}
    J -- 否 --> K[返回 401/403]
    J -- 是 --> L[返回设备/绑定/通知数据]
```

## 3. 通知发送与回执流程

```mermaid
sequenceDiagram
    participant MiniApp as 微信小程序
    participant Backend as FastAPI 后端
    participant WS as 设备 WebSocket
    participant Client as Windows 客户端

    MiniApp->>Backend: POST /api/notifications
    Note over MiniApp,Backend: Header 携带 Bearer token
    Backend->>Backend: 校验 token 与 sender_user_id
    Backend->>Backend: 校验设备归属与在线状态
    Backend->>WS: 推送 notification_created
    WS-->>Client: 通知内容
    Client-->>WS: receipt_received / receipt_displayed / receipt_spoken
    WS->>Backend: 更新 delivery_receipts
    MiniApp->>Backend: GET /api/notifications?sender_user_id=...
    Backend-->>MiniApp: 返回通知记录与投递状态
```

## 4. 关键约束

- `openid` 当前直接作为 `user_id`
- 小程序所有用户侧业务请求都必须携带 `Authorization: Bearer <session_token>`
- 后端不仅校验 token 签名，还校验该 token 已登记为活跃会话，并且 token 中解析出的用户和请求体/路径中的 `user_id` 一致
- 设备注册、心跳、WebSocket 连接仍属于客户端链路，不走小程序登录态

## 5. 注销流程

```mermaid
sequenceDiagram
    participant MiniApp as 微信小程序
    participant Backend as FastAPI 后端

    MiniApp->>Backend: POST /api/auth/logout
    Note over MiniApp,Backend: Header 携带当前 Bearer token
    Backend->>Backend: 删除活跃 session
    Backend-->>MiniApp: 204 No Content
    MiniApp->>MiniApp: 清理本地 authSession 和头像资料
```
