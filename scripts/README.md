How to run DailyEaze locally without VS Code
-------------------------------------------------

1) Start the server in the background (no VS Code needed)

  - From PowerShell run:

    powershell -ExecutionPolicy Bypass -File .\scripts\run_server.ps1

  - This starts `uvicorn app.main:app` as a detached process and writes logs to `logs/server.log`.

2) (Optional) Run at logon automatically

  - To create a Scheduled Task that starts the server when you sign in, run (requires privileges):

    powershell -ExecutionPolicy Bypass -File .\scripts\create_schtask.ps1

  - To delete the task later:

    schtasks /Delete /TN DailyEazeServer /F

Notes
  - If you use a virtual environment named `venv` in the project root, the scripts will use it automatically.
  - Ensure dependencies are installed once:

    pip install -r requirements.txt

  - The server listens on port 8000 by default: http://localhost:8000
