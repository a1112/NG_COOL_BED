@echo off
setlocal

REM Delete startup task created by create_startup_task.bat
REM Run this .bat as Administrator.

set "TASK_NAME=NG_COOL_BED_SetIP"

schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if errorlevel 1 (
  echo.
  echo Task not found: %TASK_NAME%
  echo.
  exit /b 0
)

schtasks /Delete /TN "%TASK_NAME%" /F
if errorlevel 1 (
  echo.
  echo Failed to delete task: %TASK_NAME%
  echo.
  exit /b 1
)

echo.
echo Task deleted: %TASK_NAME%
echo.

endlocal