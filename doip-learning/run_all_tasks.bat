@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Running all DoIP learning tasks...
py run_all_tasks.py --host 127.0.0.1
if errorlevel 1 (
    echo.
    echo FAILED - see messages above
    pause
    exit /b 1
)
echo.
echo SUCCESS - all tasks completed
pause
