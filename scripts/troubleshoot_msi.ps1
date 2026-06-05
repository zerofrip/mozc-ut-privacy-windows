# Diagnose MSI install issues for Mozc UT Privacy Edition.
#Requires -Version 5.1

param(
    [Parameter(Mandatory = $true)]
    [string]$MsiPath,

    [string]$LogPath = "$env:TEMP\mozc-ut-install.log"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $MsiPath)) {
    throw "MSI not found: $MsiPath"
}

$Arch = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
$IsArm64 = $env:PROCESSOR_ARCHITECTURE -eq 'ARM64'
$MsiName = [IO.Path]::GetFileName($MsiPath)

Write-Host "PC architecture   : $Arch (PROCESSOR_ARCHITECTURE=$env:PROCESSOR_ARCHITECTURE)"
Write-Host "MSI file          : $MsiName"
Write-Host "Log file          : $LogPath"
Write-Host ""

if ($IsArm64 -and $MsiName -match '-win-x64\.msi$') {
    Write-Warning @"
This is the x64 MSI. It cannot install on ARM64 Windows.
Download *-win-arm64.msi from the release page instead.
"@
}

$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
    Write-Warning 'Run this script (or the MSI) as Administrator.'
}

Write-Host 'Starting installer with verbose logging...'
$proc = Start-Process -FilePath 'msiexec.exe' -ArgumentList @(
    '/i', $MsiPath,
    '/l*v', $LogPath
) -Verb RunAs -PassThru -Wait

Write-Host "msiexec exit code : $($proc.ExitCode)"
Write-Host "Log written to    : $LogPath"

if ($proc.ExitCode -ne 0) {
    Write-Host ''
    Write-Host 'Recent errors from log:'
    Select-String -Path $LogPath -Pattern 'return value 3|error |Error ' |
        Select-Object -Last 15 |
        ForEach-Object { $_.Line }
}
