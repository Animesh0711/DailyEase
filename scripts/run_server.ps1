<#
Runs the FastAPI/Uvicorn server as a detached background process and logs output.

Usage:
  - Double-click this script in Explorer, or run from PowerShell:
      powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1

Notes:
  - If a virtual environment exists at `venv\`, the script will prefer its Python.
  - Output is written to `logs/server.log` and `logs/server.err` in the project root.
#>

$projectRoot = Split-Path -Parent $PSScriptRoot
$logs = Join-Path $projectRoot "logs"
if (!(Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

$venvPython = Join-Path $projectRoot "venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $python = "python"
}

$arguments = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"

Start-Process -FilePath $python -ArgumentList $arguments -WorkingDirectory $projectRoot -RedirectStandardOutput (Join-Path $logs "server.log") -RedirectStandardError (Join-Path $logs "server.err") -WindowStyle Hidden

Write-Output "Server started (detached). Logs: $logs\server.log"
