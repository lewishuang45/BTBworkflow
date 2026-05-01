@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title BTBworkflow Runner

set "PROMPT_1=该数据集是一个多轮次游戏的结果数据集，轮次顺序依次为 Individual、AI、CoachedAI、AugPair、Team、AugT。现在给该数据集加上一列自然排序的 ID，并去掉 Team 和 AugT 列的数据，同时针对清洗后的数据进行分组分析，按 Individual 列降序三等分，top、average、bottom 分别约占 33.3%%。"
set "PROMPT_2=根据现有 pd，分析比较三个分组的四轮数据表现，评估是否能够支持‘top 组表现一直稳定并且最后均分最高’这一结论。分析角度包括各分组分数波动、每一轮平均分数、以及 AugPair 前 33.3%% 与 top 分组的重合率，并输出高质量 JSON 分析报告。"
set "PROMPT_3=根据上一轮的 JSON 分析报告，生成一份可以用于绘制 1 页 PPT 的提纲，并准备好相关数据，最后总结成一份 JSON 文件。"

echo ============================================================
echo   BTBworkflow Runner
echo ============================================================
echo   Working folder : %cd%
echo   Input file     : sampleDATA.csv
echo   Final JSON     : final_output.json
echo   Final image    : ppt_mockup.png
echo ============================================================
echo.

call :log_time START_TIME
echo [TIME] Workflow started at !START_TIME!
echo.

if not exist "sampleDATA.csv" (
  echo [ERROR] Missing input file: sampleDATA.csv
  echo Please put the CSV in this folder and run again.
  echo.
  pause
  exit /b 1
)

if not exist ".env" (
  echo [ERROR] Missing config file: .env
  echo Please keep the generated .env file in this folder.
  echo.
  pause
  exit /b 1
)

echo [STEP 0/3] Loading Azure configuration from .env ...
for /f "usebackq tokens=* delims=" %%L in (".env") do (
  set "line=%%L"
  call :set_env
)
echo [OK] Environment variables loaded.
echo.

echo [PROMPT 1] Data cleaning and grouping instruction:
echo %PROMPT_1%
echo.
echo [PROMPT 2] Analysis instruction:
echo %PROMPT_2%
echo.
echo [PROMPT 3] PPT outline instruction:
echo %PROMPT_3%
echo.

echo [STEP 1/3] Running report stage...
echo          - Read sampleDATA.csv
echo          - Add natural ID
echo          - Remove Team and AugT
echo          - Group by Individual into top / average / bottom ^(about 33.3%% each^)
echo          - Call GPT-5.4 to generate report JSON
echo          - Save output to final_output.json
echo.
call :log_time STAGE1_START
echo [TIME] Report stage started at !STAGE1_START!
python run_workflow.py --stage report
if errorlevel 1 (
  echo.
  echo [FAILED] Report stage failed.
  echo Check the Python error above.
  echo.
  pause
  exit /b 1
)
call :log_time STAGE1_END
echo.
echo [OK] Report stage finished.
echo [TIME] Report stage ended at !STAGE1_END!
if exist "final_output.json" (
  echo [OK] Created: %cd%\final_output.json
) else (
  echo [WARNING] Report stage ended but final_output.json was not found.
)
echo.

echo [STEP 2/3] Running image stage...
echo          - Read report content from final_output.json
echo          - Convert report JSON into an image-model prompt
echo          - Call the image model to generate a 1-page PPT-style image
echo          - Save output to ppt_mockup.png
echo.
echo [NOTE] This step may take a long time depending on network and Azure response speed.
echo.
call :log_time STAGE2_START
echo [TIME] Image stage started at !STAGE2_START!
python run_workflow.py --stage image
if errorlevel 1 (
  echo.
  echo [PARTIAL SUCCESS] Image stage failed or timed out.
  echo The report JSON should already exist and can be reused.
  if exist "final_output.json" echo [OK] Existing report: %cd%\final_output.json
  echo.
  echo To retry only the image stage later, run:
  echo   python run_workflow.py --stage image
  echo.
  pause
  exit /b 1
)
call :log_time STAGE2_END
echo.
echo [OK] Image stage finished.
echo [TIME] Image stage ended at !STAGE2_END!
if exist "ppt_mockup.png" (
  echo [OK] Created: %cd%\ppt_mockup.png
) else (
  echo [WARNING] Image stage ended but ppt_mockup.png was not found.
)
echo.

echo [STEP 3/3] Workflow complete.
echo Output files:
if exist "final_output.json" echo   - %cd%\final_output.json
if exist "ppt_mockup.png" echo   - %cd%\ppt_mockup.png
call :log_time END_TIME
echo.
echo [TIME] Workflow ended at !END_TIME!
echo.
pause
exit /b 0

:set_env
if "%line%"=="" goto :eof
if "%line:~0,1%"=="#" goto :eof
for /f "tokens=1* delims==" %%A in ("%line%") do set "%%A=%%B"
goto :eof

:log_time
set "%~1=%date% %time%"
goto :eof
