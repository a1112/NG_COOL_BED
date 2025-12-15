@echo off
setlocal

REM Create/overwrite startup task to apply static IP settings at boot.
REM Run this .bat as Administrator.

set "TASK_NAME=NG_COOL_BED_SetIP"
set "SCRIPT_PATH=D:\bin\NG_COOL_BED\app\server\ip_gs\ip_set.py"
set "WAIT_SECONDS=180"

schtasks /Create ^
  /TN "%TASK_NAME%" ^
  /SC ONSTART ^
  /RU SYSTEM ^
  /RL HIGHEST ^
  /DELAY 0000:10 ^
  /F ^
  /TR "python %SCRIPT_PATH% --wait-seconds %WAIT_SECONDS%"

echo.
echo Task created/updated: %TASK_NAME%
echo.
schtasks /Query /TN "%TASK_NAME%" /V /FO LIST

endlocal

