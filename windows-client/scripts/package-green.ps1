<#
.SYNOPSIS
    Windows 客户端绿色版打包脚本

.DESCRIPTION
    执行 dotnet publish 生成 self-contained 绿色版 zip 包。
    通过环境变量 SCHOOL_NOTIFY_BASE_URL 指定后端地址。

.PARAMETER Version
    版本号，如 "1.0.3"

.PARAMETER BaseUrl
    后端服务器地址

.PARAMETER Environment
    打包环境：test（默认）或 prod
    - test → 输出到 artifacts/publish/windows-client/<version>/
    - prod → 输出到 artifacts/<version>/

.EXAMPLE
    .\scripts\package-green.ps1 -Version "1.0.3" -BaseUrl "http://test-server:8000"
    .\scripts\package-green.ps1 -Version "1.0.3" -BaseUrl "https://prod.example.com" -Environment prod
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Version,

    [Parameter(Mandatory = $true)]
    [string]$BaseUrl,

    [ValidateSet("test", "prod")]
    [string]$Environment = "test"
)

$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $PSScriptRoot
$project    = Join-Path $projectDir "src\SchoolNotify.WindowsClient\SchoolNotify.WindowsClient.csproj"

if ($Environment -eq "prod") {
    $outputBase = Join-Path $projectDir "artifacts"
} else {
    $outputBase = Join-Path $projectDir "artifacts\publish\windows-client"
}

$publishDir = Join-Path $outputBase $Version
$zipPath    = Join-Path $outputBase "school-notify-windows-client-$Version.zip"

$env:SCHOOL_NOTIFY_BASE_URL = $BaseUrl.TrimEnd('/')

Write-Host "Environment: $Environment"
Write-Host "BaseUrl:     $env:SCHOOL_NOTIFY_BASE_URL"
Write-Host "Output:      $outputBase"
Write-Host ""

if (Test-Path $publishDir) { Remove-Item $publishDir -Recurse -Force }
if (Test-Path $zipPath)    { Remove-Item $zipPath -Force }

Write-Host "Cleaning..."
dotnet clean $project -c Release -r win-x64 | Out-Null

Write-Host "Publishing $Version..."
dotnet publish $project `
    -c Release `
    -r win-x64 `
    --self-contained true `
    "-p:Version=$Version" `
    "-p:AssemblyVersion=$Version.0" `
    "-p:FileVersion=$Version.0" `
    "-p:InformationalVersion=$Version" `
    -p:PublishSingleFile=false `
    -p:UseAppHost=true `
    -o $publishDir

if ($LASTEXITCODE -ne 0) {
    Write-Error "dotnet publish failed with exit code $LASTEXITCODE"
    exit 1
}

$dll = Join-Path $publishDir "SchoolNotify.WindowsClient.dll"
if (-not (Test-Path $dll)) {
    Write-Error "DLL not found in publish output: $dll"
    exit 1
}

$asm  = [System.Reflection.AssemblyName]::GetAssemblyName($dll)
$info = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($dll)

Write-Host ""
Write-Host "Version check:"
Write-Host "  AssemblyVersion = $($asm.Version)"
Write-Host "  FileVersion     = $($info.FileVersion)"
Write-Host "  ProductVersion  = $($info.ProductVersion)"

if ($asm.Version -ne "$Version.0") {
    Write-Error "AssemblyVersion mismatch: expected $Version.0, got $($asm.Version)"
    exit 1
}

Write-Host ""
Write-Host "Compressing..."
Compress-Archive -Path "$publishDir\*" -DestinationPath $zipPath -Force

$zip = Get-Item $zipPath
Write-Host ""
Write-Host "Done!"
Write-Host "  DIR: $publishDir"
Write-Host "  ZIP: $($zip.FullName)"
Write-Host "  Size: $([math]::Round($zip.Length / 1MB, 2)) MB"
