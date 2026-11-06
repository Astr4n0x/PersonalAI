@echo off
REM Run Jarvis with the project's virtual environment
cd /d "%~dp0"
.venv\Scripts\python.exe main.py
pause
