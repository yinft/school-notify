# Windows Client

Windows WPF 客户端，功能：

1. 设备注册与心跳
2. 绑定码 / 二维码展示
3. WebSocket 实时连接
4. 横幅和语音通知
5. 系统托盘与开机自启
6. 绿色版自动更新

## 本地构建

开发调试构建：

```powershell
dotnet build SchoolNotify.WindowsClient.sln
```

调试/构建输出目录由 `Directory.Build.props` 固定到：

```text
windows-client/artifacts/bin/
windows-client/artifacts/obj/
```

## 服务器地址

客户端通过环境变量 `SCHOOL_NOTIFY_BASE_URL` 读取后端地址。

- **本地调试**：不设置该变量时默认 `http://127.0.0.1:8000`
- **打包时**：由 `package-green.ps1` 通过 `-BaseUrl` 参数自动设置

## 绿色版打包

使用 `scripts/package-green.ps1` 一键打包。

### 使用方法

```powershell
# 测试包（指向测试服务器）
.\scripts\package-green.ps1 -Version "1.0.3" -BaseUrl "http://test-server:8000"

# 生产包（指向正式服务器）
.\scripts\package-green.ps1 -Version "1.0.3" -BaseUrl "https://your-domain.com"
```

### 脚本做了什么

1. 设置环境变量 `SCHOOL_NOTIFY_BASE_URL` 为传入的地址
2. `dotnet clean` + `dotnet publish` (self-contained, win-x64)
3. 校验 DLL 版本与 `-Version` 参数一致
4. 压缩为 zip

### 产出

```text
windows-client/artifacts/publish/windows-client/<version>/
windows-client/artifacts/publish/windows-client/school-notify-windows-client-<version>.zip
```

### 版本校验

脚本自动校验 DLL 版本。如果版本不匹配会报错并终止，不会生成 zip。

输出示例：

```text
Version check:
  AssemblyVersion = 1.0.3.0
  FileVersion     = 1.0.3.0
  ProductVersion  = 1.0.3+abc123...

Done!
  ZIP:  ...\school-notify-windows-client-1.0.3.zip
  Size: 67.87 MB
```
