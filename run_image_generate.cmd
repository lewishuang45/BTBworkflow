@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
title BTBworkflow Image Generation Runner

echo ============================================================
echo   BTBworkflow Image Generation Runner
echo ============================================================
echo   Working folder : %cd%
echo   Input JSON     : final_output.json
echo   Output image   : ppt_mockup.png
echo ============================================================
echo.

if not exist ".env" (
  echo [ERROR] Missing .env
  pause
  exit /b 1
)

if not exist "final_output.json" (
  echo [ERROR] Missing final_output.json
  echo Please run report stage first.
  pause
  exit /b 1
)

echo [STEP 1/2] Running image stage directly...
echo [INFO] Manual probe is available separately via: python probe_image2.py
echo [INFO] If this step is slow, watch image_stage_debug.log for progress.
python run_workflow.py --stage image 1> image_stage_debug.log 2>&1
if errorlevel 1 (
  echo [FAILED] Image stage failed.
  echo --- Last log lines ---
  powershell -Command "Get-Content image_stage_debug.log -Tail 40"
  pause
  exit /b 1
)
echo [OK] Image stage finished.
echo.

echo [STEP 2/2] Checking output...
if exist "ppt_mockup.png" (
  echo [OK] Created: %cd%\ppt_mockup.png
) else (
  echo [FAILED] ppt_mockup.png was not found.
  echo --- Last log lines ---
  powershell -Command "Get-Content image_stage_debug.log -Tail 40"
  pause
  exit /b 1
)

echo.
echo [DONE] Image generation workflow finished.
pause
exit /b 0
