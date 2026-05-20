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

推荐每次打包时显式传入版本号，避免后台版本号已更新但 zip 内程序集仍是旧版本。

以下示例打包 `1.0.1`：

```powershell
$version = "1.0.1"
$publishDir = "artifacts\publish\windows-client\$version"
$zipPath = "artifacts\publish\windows-client\school-notify-windows-client-$version.zip"

if (Test-Path $publishDir) { Remove-Item $publishDir -Recurse -Force }
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

dotnet clean src\SchoolNotify.WindowsClient\SchoolNotify.WindowsClient.csproj `
  -c Release `
  -r win-x64

dotnet publish src\SchoolNotify.WindowsClient\SchoolNotify.WindowsClient.csproj `
  -c Release `
  -r win-x64 `
  --self-contained true `
  -p:Version=$version `
  -p:AssemblyVersion=$version.0 `
  -p:FileVersion=$version.0 `
  -p:InformationalVersion=$version `
  -p:PublishSingleFile=false `
  -p:UseAppHost=true `
  -o $publishDir

Compress-Archive `
  -Path "$publishDir\*" `
  -DestinationPath $zipPath `
  -Force
```

输出目录：

```text
windows-client/artifacts/publish/windows-client/1.0.1/
```

zip 包路径：

```text
windows-client/artifacts/publish/windows-client/school-notify-windows-client-1.0.1.zip
```

打包后应确认 zip 内至少包含：

```text
SchoolNotify.WindowsClient.exe
server-config.json
```

### 版本校验

上传 zip 前必须校验包内 DLL 版本，确保它与后台配置的 `latest_version` 一致：

```powershell
$dll = Resolve-Path "$publishDir\SchoolNotify.WindowsClient.dll"
$asm = [System.Reflection.AssemblyName]::GetAssemblyName($dll)
$info = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($dll)

"AssemblyVersion=$($asm.Version)"
"FileVersion=$($info.FileVersion)"
"ProductVersion=$($info.ProductVersion)"
```

例如打包 `1.0.1` 时，应看到类似：

```text
AssemblyVersion=1.0.1.0
FileVersion=1.0.1.0
ProductVersion=1.0.1+...
```

如果这里仍显示 `0.1.0`，说明包内容是旧版本；不要上传这个 zip。

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
