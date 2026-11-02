@echo off
rem Emergency stop for optional third-party global click debounce helper.
rem Firefly itself does NOT install system-wide mouse hooks.
taskkill /IM MouseDebouncer64.exe /F >nul 2>&1
if errorlevel 1 (
  echo MouseDebouncer64.exe was not running, or could not be stopped.
) else (
  echo Global Windows mouse debounce stopped. Ordinary clicks restored.
)
pause
