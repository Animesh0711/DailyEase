<#
Create a Windows Scheduled Task that runs the `run_server.ps1` script at user logon.

Usage (requires appropriate privileges):
  powershell -ExecutionPolicy Bypass -File .\scripts\create_schtask.ps1

This creates a task named `DailyEazeServer` which executes the run script at each logon.
#>

$projectRoot = Split-Path -Parent $PSScriptRoot
$scriptPath = Join-Path $projectRoot "scripts\run_server.ps1"
$taskName = "DailyEazeServer"

$action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"$scriptPath\""

Write-Output "Creating scheduled task: $taskName"
schtasks /Create /SC ONLOGON /RL HIGHEST /TN $taskName /TR $action /F

Write-Output "Scheduled task '$taskName' created. To remove it use: schtasks /Delete /TN $taskName /F"
