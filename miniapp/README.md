# Miniapp

微信小程序端，用于绑定桌面客户端、发送设备提醒、查看发送记录。当前包含：

1. 应用入口
2. 设备列表页
3. 发送提醒页
4. 基础请求封装

建议使用微信开发者工具打开 `miniapp` 目录。

## 登录说明

当前小程序启动后会自动调用 `wx.login`，再由后端 `POST /api/auth/login` 换取微信 `openid`。

用户点击“注销当前登录”后，小程序会先调用后端 `POST /api/auth/logout` 撤销当前 session，再清理本地登录态。

请确保后端已在 `backend/.env` 中配置好数据库和微信参数。

因此在联调前，需要先确保后端已经配置：

```bash
SCHOOL_NOTIFY_WECHAT_APP_ID=<你的小程序 appid>
SCHOOL_NOTIFY_WECHAT_APP_SECRET=<你的小程序 secret>
```
