# Uninstall Mozc UT Privacy Edition portable build.
#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

$InstallDir = Join-Path $env:LOCALAPPDATA 'MozcUTPrivacy'
if (Test-Path $InstallDir) {
    Remove-Item -Recurse -Force $InstallDir
    Write-Host "Removed $InstallDir"
} else {
    Write-Host "Nothing to remove."
}
