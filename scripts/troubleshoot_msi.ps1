# Diagnose MSI install issues for Mozc UT Privacy Edition.
#Requires -Version 5.1

param(
    [Parameter(Mandatory = $true)]
    [string]$MsiPath,

    [string]$LogPath = "$env:TEMP\mozc-ut-install.log"
)

$ErrorActionPreference = 'Stop'

$UpgradeCode = '{A7F3E2B1-8C4D-4E5F-9A6B-1C2D3E4F5A6B}'

function Write-Section([string]$Title) {
    Write-Host ''
    Write-Host "=== $Title ==="
}

function Get-InstalledMozcUtProducts {
    $roots = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )
    foreach ($root in $roots) {
        Get-ItemProperty $root -ErrorAction SilentlyContinue |
            Where-Object {
                $_.DisplayName -like '*Mozc UT Privacy*' -or
                $_.UpgradeCode -eq $UpgradeCode
            } |
            Select-Object DisplayName, DisplayVersion, PSChildName, UninstallString
    }
}

function Get-OsBuildNumber {
    try {
        $cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
        return [int]$cv.CurrentBuildNumber
    }
    catch {
        return $null
    }
}

function Interpret-Log([string]$Path) {
    if (-not (Test-Path $Path)) {
        Write-Warning "Log file not found: $Path"
        return
    }

    $patterns = @{
        'Already installed (maintenance mode, no changes)' = 'entering maintenance mode|Action: Null|構成を正しく完了しました'
        'Launch condition failed' = 'LaunchCondition|return value 3.*LaunchConditions'
        'Newer version already installed' = 'NEWERVERSIONDETECTED|NewerVersionError|error 4000'
        'Administrator required' = 'Privileged|管理者権限'
        'OS version too old' = 'OS_BUILD_NUMBER|1809|17763'
        'Wrong architecture (ARM64 PC + x64 MSI)' = 'PROCESSOR_ARCHITECTURE.*ARM64|ARM64 環境|x64 専用'
        'Generic MSI failure' = 'return value 3|Installation success or error status: 1603'
    }

    foreach ($entry in $patterns.GetEnumerator()) {
        $hit = Select-String -Path $Path -Pattern $entry.Value -CaseSensitive:$false |
            Select-Object -First 1
        if ($hit) {
            Write-Host "  [$($entry.Key)]"
            Write-Host "    $($hit.Line.Trim())"
        }
    }

    Write-Host ''
    Write-Host 'Last 20 log lines:'
    Get-Content $Path -Tail 20 | ForEach-Object { Write-Host "  $_" }
}

if (-not (Test-Path $MsiPath)) {
    throw "MSI not found: $MsiPath"
}

$Arch = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
$Build = Get-OsBuildNumber
$IsArm64 = $env:PROCESSOR_ARCHITECTURE -eq 'ARM64'
$MsiName = [IO.Path]::GetFileName($MsiPath)
$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Section 'Environment'
Write-Host "PC architecture        : $Arch (PROCESSOR_ARCHITECTURE=$env:PROCESSOR_ARCHITECTURE)"
Write-Host "OS build number        : $Build"
Write-Host "Running as admin       : $IsAdmin"
Write-Host "MSI file               : $MsiName"
Write-Host "Log file               : $LogPath"

Write-Section 'Pre-flight checks'
if ($IsArm64 -and $MsiName -match '-win-x64\.msi$') {
    Write-Warning @"
ARM64 PC に x64 専用 MSI を実行しています。
Release ページから *-win-arm64.msi をダウンロードしてください。
"@
}
elseif (-not $IsArm64 -and $MsiName -match '-win-arm64\.msi$') {
    Write-Warning 'x64 PC に ARM64 MSI を実行しています。*-win-x64.msi を使用してください。'
}

if ($Build -and $Build -lt 17763) {
    Write-Warning "Windows 10 1809 (build 17763) 以降が必要です。現在の build: $Build"
}

if (-not $IsAdmin) {
    Write-Warning @"
管理者権限がありません。UAC の「はい」を選んで再実行します。
通常のダブルクリックでは権限不足で終了することがあります。
"@
}

$installed = @(Get-InstalledMozcUtProducts)
if ($installed.Count -gt 0) {
    Write-Host 'Detected existing Mozc UT Privacy Edition install(s):'
    $installed | ForEach-Object {
        Write-Host "  - $($_.DisplayName) $($_.DisplayVersion)"
    }
    Write-Host 'より新しいバージョンが入っている場合、インストーラは終了します。'
    Write-Host '設定 → アプリ から既存版をアンインストールしてから再試行してください。'
}
else {
    Write-Host 'No existing Mozc UT Privacy Edition install found in Add/Remove Programs.'
}

Write-Section 'Running installer (elevated, verbose log)'
if (Test-Path $LogPath) {
    Remove-Item $LogPath -Force
}

$proc = Start-Process -FilePath 'msiexec.exe' -ArgumentList @(
    '/i', $MsiPath,
    '/l*v', $LogPath
) -Verb RunAs -PassThru -Wait

Write-Host "msiexec exit code      : $($proc.ExitCode)"

$exitHints = @{
    0 = 'Success'
    1602 = 'User cancelled'
    1603 = 'Fatal error during install (see log)'
    1618 = 'Another install is already in progress'
    1638 = 'Same or newer version already installed'
}
if ($exitHints.ContainsKey($proc.ExitCode)) {
    Write-Host "Meaning                 : $($exitHints[$proc.ExitCode])"
}

Write-Section 'Log analysis'
Interpret-Log -Path $LogPath

if ($proc.ExitCode -ne 0) {
    Write-Host ''
    Write-Host "Full log: $LogPath"
    Write-Host 'Issue を報告するときはこのログファイルを添付してください。'
}
