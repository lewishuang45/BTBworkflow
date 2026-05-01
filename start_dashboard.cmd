@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title BTBworkflow Dashboard Server

echo Cleaning stale port 8000 processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
  taskkill /PID %%a /F >nul 2>nul
)

echo Starting local dashboard...
echo URL: http://127.0.0.1:8000
echo.
python webapp.py

pause
