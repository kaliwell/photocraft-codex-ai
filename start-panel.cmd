@echo off
cd /d "%~dp0"
where pythonw >nul 2>nul
if errorlevel 1 (
  python -m photocraft_ai %*
  pause
) else (
  start "" pythonw -m photocraft_ai %*
)
