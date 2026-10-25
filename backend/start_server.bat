@echo off
cd /d "%~dp0"
echo ========================================================
echo   GetGoals PCAT + NCD Adaptive Placement Engine
echo   API Server running on: http://127.0.0.1:8000
echo ========================================================
.venv\Scripts\python.exe pcat_server.py
pause
