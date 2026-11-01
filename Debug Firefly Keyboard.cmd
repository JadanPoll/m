@echo off
setlocal
cd /d "%~dp0"
echo Launching Firefly with visible diagnostics; Windows OSK stays available.
echo Startup log: %%LOCALAPPDATA%%\FireflyDeskKeyboard\startup.log
python -u "%~dp0firefly_keyboard.pyw"
set "FIREFLY_CODE=%ERRORLEVEL%"
echo.
echo Firefly exited. Python exit code: %FIREFLY_CODE%
echo See %%LOCALAPPDATA%%\FireflyDeskKeyboard\startup.log for recorded errors.
pause
