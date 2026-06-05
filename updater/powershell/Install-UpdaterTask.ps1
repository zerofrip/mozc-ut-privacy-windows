# Register a daily scheduled task for the Mozc UT Privacy Edition updater.
#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

param(
    [string]$UpdaterPath = "$env:ProgramFiles\MozcUTPrivacy\MozcUTUpdater.exe"
)

$TaskName = 'MozcUTPrivacyUpdater'
$Action = New-ScheduledTaskAction -Execute $UpdaterPath -Argument '--check-now'
$Trigger = New-ScheduledTaskTrigger -Daily -At '03:00'
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Principal $Principal -Settings $Settings -Force

Write-Host "Registered scheduled task: $TaskName"
