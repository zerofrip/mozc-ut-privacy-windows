# Install Mozc UT Privacy Edition portable build for the current user.
#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

$InstallDir = Join-Path $env:LOCALAPPDATA 'MozcUTPrivacy'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (Test-Path $InstallDir) {
    Write-Host "Removing existing installation at $InstallDir"
    Remove-Item -Recurse -Force $InstallDir
}

Copy-Item -Recurse $ScriptDir $InstallDir
Write-Host "Installed to $InstallDir"
Write-Host "Register the IME using Windows Settings > Time & Language > Language & Region."
