# school-notify

桌面设备提醒系统单仓项目。

项目用于向本人绑定的桌面客户端发送提醒消息，帮助用户在多设备场景下同步重要事项。

## 目录

- `backend`：FastAPI 后端
- `miniapp`：微信小程序
- `windows-client`：Windows WPF 桌面端
- `docs`：PRD 和设计文档

## 当前状态

当前仓库已完成：

1. PRD 文档基线
2. 三端项目骨架
3. 后端最小可运行入口

## 开发约定

1. 后端使用 `uv` 和项目内 `backend/.venv`
2. 不直接使用主机 Python 环境安装依赖
3. 微信小程序使用微信开发者工具打开 `miniapp`
4. Windows 客户端使用 Visual Studio 或 .NET SDK 打开 `windows-client`

## 常用命令

### 后端

```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload
uv run pytest
```

### Windows 客户端

```bash
cd windows-client
dotnet build SchoolNotify.WindowsClient.sln
```
