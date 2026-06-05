# Build Mozc UT Privacy Edition for Windows.
#Requires -Version 5.1

param(
    [ValidateSet('x64', 'arm64')]
    [string]$Architecture = 'x64'
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$MozcSrc = Join-Path $RepoRoot 'vendor\mozc\src'

Push-Location $MozcSrc
try {
    Write-Host "Installing Mozc dependencies..."
    python build_tools/update_deps.py

    Write-Host "Building Qt..."
    python build_tools/build_qt.py --release --confirm_license

    if (Test-Path 'third_party\qt_src') {
        Write-Host "Removing Qt source to save disk space..."
        Remove-Item -Recurse -Force 'third_party\qt_src'
    }

    $BazelArgs = @(
        'build',
        '--config', 'oss_windows',
        '--config', 'release_build',
        'package',
        '--verbose_failures'
    )

    if ($Architecture -eq 'arm64') {
        $BazelArgs += @('--platforms=//:windows-arm64')
    }

    Write-Host "Building Mozc ($Architecture)..."
    bazelisk @BazelArgs

    $MsiPath = Join-Path $MozcSrc 'bazel-bin\win32\installer\MozcUTPrivacy64.msi'
    if (-not (Test-Path $MsiPath)) {
        throw "MSI not found at $MsiPath"
    }
    Write-Host "Build complete: $MsiPath"
}
finally {
    Pop-Location
}
