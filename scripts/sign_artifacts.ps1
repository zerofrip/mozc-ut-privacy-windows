# Sign release artifacts when code signing credentials are available.
#Requires -Version 5.1

param(
    [Parameter(Mandatory = $true)]
    [string[]]$Files
)

$ErrorActionPreference = 'Stop'

$CertBase64 = $env:WINDOWS_CODE_SIGNING_CERT_BASE64
$CertPassword = $env:WINDOWS_CODE_SIGNING_CERT_PASSWORD
$TimestampUrl = if ($env:WINDOWS_CODE_SIGNING_TIMESTAMP_URL) {
    $env:WINDOWS_CODE_SIGNING_TIMESTAMP_URL
} else {
    'http://timestamp.digicert.com'
}

if (-not $CertBase64) {
    Write-Host 'No signing certificate configured; skipping code signing.'
    return
}

$CertPath = Join-Path $env:RUNNER_TEMP 'codesign.pfx'
[IO.File]::WriteAllBytes($CertPath, [Convert]::FromBase64String($CertBase64))

$SignTool = Get-ChildItem -Path "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Recurse -Filter 'signtool.exe' |
    Sort-Object FullName -Descending |
    Select-Object -First 1

if (-not $SignTool) {
    throw 'signtool.exe not found. Install the Windows SDK.'
}

foreach ($File in $Files) {
    if (-not (Test-Path $File)) {
        Write-Warning "Skipping missing file: $File"
        continue
    }
    Write-Host "Signing $File"
    & $SignTool.FullName sign /fd SHA256 /f $CertPath /p $CertPassword /tr $TimestampUrl /td SHA256 $File
    & $SignTool.FullName verify /pa $File
}
