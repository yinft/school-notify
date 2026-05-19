# Windows Client

Windows WPF 客户端骨架，目标能力：

1. 设备注册
2. 绑定码展示
3. WebSocket 在线连接
4. 横幅和卡片提醒
5. 系统托盘与开机自启

当前环境未安装 .NET SDK，本仓库已生成项目文件，但尚未在本机编译验证。

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

推荐使用固定输出路径生成绿色版自包含包：

```powershell
dotnet publish src\SchoolNotify.WindowsClient\SchoolNotify.WindowsClient.csproj `
  -c Release `
  -r win-x64 `
  --self-contained true `
  -p:PublishSingleFile=false `
  -p:UseAppHost=true `
  -o artifacts\SchoolNotify.WindowsClient-green-self-contained-win-x64

Compress-Archive `
  -Path artifacts\SchoolNotify.WindowsClient-green-self-contained-win-x64\* `
  -DestinationPath artifacts\SchoolNotify.WindowsClient-green-self-contained-win-x64.zip `
  -Force
```

固定输出目录：

```text
windows-client/artifacts/SchoolNotify.WindowsClient-green-self-contained-win-x64/
```

固定 zip 包路径：

```text
windows-client/artifacts/SchoolNotify.WindowsClient-green-self-contained-win-x64.zip
```

打包后应确认 zip 内至少包含：

```text
SchoolNotify.WindowsClient.exe
server-config.json
```

## 推荐后续脚本化

后续可以新增：

```text
windows-client/scripts/package-green.ps1
```

脚本职责：

1. 清理旧的绿色版发布目录。
2. 执行 `dotnet publish`。
3. 压缩生成固定 zip。
4. 校验 `SchoolNotify.WindowsClient.exe` 和 `server-config.json` 存在。
5. 输出最终 zip 路径和大小。
