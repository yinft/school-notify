<#
.SYNOPSIS
    Windows 客户端绿色版打包脚本

.DESCRIPTION
    执行 dotnet publish 生成 self-contained 绿色版 zip 包。
    打包前自动替换 server-config.json 中的 BaseUrl，打包后恢复原值。

.EXAMPLE
    .\scripts\package-green.ps1 -Version "1.0.3" -BaseUrl "http://test-server:8000"
    .\scripts\package-green.ps1 -Version "1.0.3" -BaseUrl "https://prod.example.com"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Version,

    [Parameter(Mandatory = $true)]
    [string]$BaseUrl
)

$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $PSScriptRoot
$configFile = Join-Path $projectDir "src\SchoolNotify.WindowsClient\server-config.json"
$project    = Join-Path $projectDir "src\SchoolNotify.WindowsClient\SchoolNotify.WindowsClient.csproj"
$publishDir = Join-Path $projectDir "artifacts\publish\windows-client\$Version"
$zipPath    = Join-Path $projectDir "artifacts\publish\windows-client\school-notify-windows-client-$Version.zip"

if (-not (Test-Path $configFile)) {
    Write-Error "server-config.json not found: $configFile"
    exit 1
}

$originalConfig = Get-Content -LiteralPath $configFile -Raw

try {
    @"
{
  "BaseUrl": "$($BaseUrl.TrimEnd('/'))"
}
"@ | Set-Content -LiteralPath $configFile -Encoding UTF8

    Write-Host "BaseUri set to: $($BaseUrl.TrimEnd('/'))"

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
    Write-Host "  ZIP:  $($zip.FullName)"
    Write-Host "  Size: $([math]::Round($zip.Length / 1MB, 2)) MB"
}
finally {
    Set-Content -LiteralPath $configFile -Value $originalConfig -Encoding UTF8
    Write-Host ""
    Write-Host "server-config.json restored."
}
