# Package a portable ZIP from Mozc build outputs.
#Requires -Version 5.1

param(
    [Parameter(Mandatory = $true)]
    [string]$Version,

    [ValidateSet('x64', 'arm64')]
    [string]$Architecture = 'x64',

    [Parameter(Mandatory = $true)]
    [string]$OutputDir
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$MozcSrc = Join-Path $RepoRoot 'vendor\mozc\src'
$BazelBin = Join-Path $MozcSrc 'bazel-bin'

$Staging = Join-Path $env:TEMP "mozc-ut-portable-$Architecture"
if (Test-Path $Staging) {
    Remove-Item -Recurse -Force $Staging
}
New-Item -ItemType Directory -Path $Staging | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Staging 'doc') | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Staging 'platforms') | Out-Null

function Copy-IfExists($Source, $Dest) {
    if (Test-Path $Source) {
        Copy-Item $Source $Dest
    } else {
        Write-Warning "Missing file: $Source"
    }
}

$Files = @(
    @{ Src = 'server\mozc_server.exe'; Dst = 'mozc_server.exe' },
    @{ Src = 'win32\broker\mozc_broker.exe'; Dst = 'mozc_broker.exe' },
    @{ Src = 'win32\cache_service\mozc_cache_service.exe'; Dst = 'mozc_cache_service.exe' },
    @{ Src = 'win32\tip\mozc_tip32.dll'; Dst = 'mozc_tip32.dll' },
    @{ Src = 'win32\tip\mozc_tip64.dll'; Dst = 'mozc_tip64.dll' },
    @{ Src = 'gui\tool\mozc_tool.exe'; Dst = 'mozc_tool.exe' },
    @{ Src = 'renderer\win32\mozc_renderer.exe'; Dst = 'mozc_renderer.exe' }
)

foreach ($File in $Files) {
    Copy-IfExists (Join-Path $BazelBin $File.Src) (Join-Path $Staging $File.Dst)
}

$QtBin = Join-Path $MozcSrc 'third_party\qt\bin'
foreach ($Dll in @('Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll')) {
    Copy-IfExists (Join-Path $QtBin $Dll) (Join-Path $Staging $Dll)
}
Copy-IfExists (Join-Path $QtBin '..\plugins\platforms\qwindows.dll') (Join-Path $Staging 'platforms\qwindows.dll')

$DocDir = Join-Path $MozcSrc 'data\installer'
foreach ($Doc in @('LICENSES.txt', 'THIRD_PARTY_LICENSES.txt', 'CREDITS.txt', 'credits_en.html')) {
    Copy-IfExists (Join-Path $DocDir $Doc) (Join-Path $Staging "doc\$Doc")
}

$VersionJson = @{
    product = 'Mozc UT Privacy Edition'
    version = $Version
    architecture = $Architecture
    build_date = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
} | ConvertTo-Json
Set-Content -Path (Join-Path $Staging 'VERSION.json') -Value $VersionJson -Encoding UTF8

Copy-Item (Join-Path $RepoRoot 'scripts\templates\install-portable.ps1') (Join-Path $Staging 'install-portable.ps1')
Copy-Item (Join-Path $RepoRoot 'scripts\templates\uninstall-portable.ps1') (Join-Path $Staging 'uninstall-portable.ps1')

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$ZipName = "MozcUTPrivacy-$Version-win-$Architecture-portable.zip"
$ZipPath = Join-Path $OutputDir $ZipName
if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
Compress-Archive -Path (Join-Path $Staging '*') -DestinationPath $ZipPath
Write-Host "Created portable package: $ZipPath"
