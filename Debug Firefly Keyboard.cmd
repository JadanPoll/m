@echo off
setlocal
cd /d "%~dp0"
echo Launching Firefly with a visible diagnostic console; Windows OSK stays available.
echo Startup log: %LOCALAPPDATA%\FireflyDeskKeyboard\startup.log
python -u "%~dp0firefly_keyboard.pyw" --debug-console
set "FIREFLY_CODE=%ERRORLEVEL%"
echo.
echo Firefly exited. Python exit code: %FIREFLY_CODE%
echo The startup log is also saved under LocalAppData\FireflyDeskKeyboard.
pause
