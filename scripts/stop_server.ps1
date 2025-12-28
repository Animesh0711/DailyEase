<#
Stops the detached Uvicorn/FastAPI server started by `run_server.ps1`.

Usage:
  powershell -ExecutionPolicy Bypass -File .\scripts\stop_server.ps1

This script attempts to find Python processes running `uvicorn` (or `app.main:app`) and stops them.
It will also attempt to stop processes by listening port 8000 if available.
#>

$stopped = $false

Write-Output "Searching for uvicorn/python processes..."

try {
    # Prefer querying WMI/CIM to inspect commandline for uvicorn
    $procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and ($_.CommandLine -match 'uvicorn' -or $_.CommandLine -match 'app.main:app') }
    if ($procs -and $procs.Count -gt 0) {
        foreach ($p in $procs) {
            Write-Output "Stopping process Id=$($p.ProcessId) CommandLine=$($p.CommandLine)"
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
            $stopped = $true
        }
    }
} catch {
    Write-Output "WMI/CIM query failed: $_"
}

if (-not $stopped) {
    # Fallback: attempt to stop python processes that may be running uvicorn
    $pyProcs = Get-Process -Name python -ErrorAction SilentlyContinue
    if ($pyProcs) {
        foreach ($pp in $pyProcs) {
            try {
                $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($pp.Id)").CommandLine
                if ($cmd -and ($cmd -match 'uvicorn' -or $cmd -match 'app.main:app')) {
                    Write-Output "Stopping python process Id=$($pp.Id) CommandLine=$cmd"
                    Stop-Process -Id $pp.Id -Force -ErrorAction SilentlyContinue
                    $stopped = $true
                }
            } catch { }
        }
    }
}

if (-not $stopped) {
    Write-Output "No uvicorn/python processes found by commandline. Trying to free port 8000 (if held by a process)."
    try {
        # Find process holding port 8000 via netstat and stop it
        $net = netstat -ano | Select-String ":8000"
        if ($net) {
            foreach ($line in $net) {
                $parts = ($line -split '\s+') | Where-Object { $_ -ne '' }
                $pid = $parts[-1]
                if ($pid -and $pid -match '^[0-9]+$') {
                    Write-Output "Stopping process Id=$pid (held 8000)"
                    Stop-Process -Id [int]$pid -Force -ErrorAction SilentlyContinue
                    $stopped = $true
                }
            }
        }
    } catch { }
}

if ($stopped) {
    Write-Output "Server stop attempted. Verify with: Get-Process -Name python -ErrorAction SilentlyContinue or curl http://localhost:8000"
} else {
    Write-Output "No matching server process found. If the server is still running, consider checking Task Manager or run manually: Get-Process -Name python | Stop-Process"
}
