@echo off
setlocal
rem OPTIONAL global Windows left-click chatter filter. NOT launched by Firefly.
rem Read docs/desktop-ok-debounce.md before enabling in a remote-only session.
set "FILTER=%~dp0tools\MouseDebouncer64.exe"
if not exist "%FILTER%" set "FILTER=%~dp0MouseDebouncer64.exe"
if not exist "%FILTER%" (
  echo MouseDebouncer64.exe not found.
  echo Download its release from https://github.com/marvinlehmann/Mouse-Debouncer/releases
  echo Place it next to this script or inside the tools directory.
  echo No global hook has been started.
  pause
  exit /b 1
)
tasklist /FI "IMAGENAME eq MouseDebouncer64.exe" 2>nul | find /I "MouseDebouncer64.exe" >nul
if not errorlevel 1 (
  echo Desktop OK filter already appears to be running. Nothing started.
  pause
  exit /b 0
)
echo Starting optional GLOBAL Windows left-click debounce at 220 ms.
echo This affects ALL desktop applications until the filter exits.
echo To stop, run "Stop Desktop OK Debounce.cmd".
start "" "%FILTER%" --left=220 -q
