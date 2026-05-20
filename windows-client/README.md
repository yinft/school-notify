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

## 绿色版打包

使用 `scripts/package-green.ps1` 一键打包，自动处理 `server-config.json` 的地址切换。

### 使用方法

```powershell
# 测试包（指向测试服务器）
.\scripts\package-green.ps1 -Version "1.0.3" -BaseUrl "http://test-server:8000"

# 生产包（指向正式服务器）
.\scripts\package-green.ps1 -Version "1.0.3" -BaseUrl "https://your-domain.com"
```

### 脚本做了什么

1. 备份当前 `src/SchoolNotify.WindowsClient/server-config.json`
2. 将 `BaseUrl` 替换为传入的地址
3. `dotnet clean` + `dotnet publish` (self-contained, win-x64)
4. 校验 DLL 版本与 `-Version` 参数一致
5. 压缩为 zip
6. **恢复** `server-config.json` 为原始内容

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
