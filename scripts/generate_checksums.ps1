# Generate SHA256 checksums for release artifacts.
#Requires -Version 5.1

param(
    [Parameter(Mandatory = $true)]
    [string]$OutputFile,

    [Parameter(Mandatory = $true)]
    [string[]]$Files
)

$ErrorActionPreference = 'Stop'

$Lines = @()
foreach ($File in $Files) {
    if (-not (Test-Path $File)) {
        throw "File not found: $File"
    }
    $Hash = Get-FileHash -Algorithm SHA256 -Path $File
    $Name = Split-Path -Leaf $File
    $Lines += "$($Hash.Hash.ToLower())  $Name"
}

Set-Content -Path $OutputFile -Value ($Lines -join "`n") -Encoding UTF8
Write-Host "Wrote checksums to $OutputFile"
