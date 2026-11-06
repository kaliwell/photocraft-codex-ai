@echo off
cd /d "%~dp0"
"%~dp0python\python.exe" "%~dp0portable_launcher.py" --clean-cache
pause
