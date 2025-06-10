@echo off
setlocal

set UI_MODE=1
set LOOPRANGE=5
set USER=abraham
set HEADLESS=1

:: Time limit in minutes
set MAX_RUNTIME_MINUTES=600
set INTERVAL_MINUTES=3
set /a INTERVAL_SECONDS=%INTERVAL_MINUTES% * 60

:: Start asyncserve.py in a new terminal
:: start "Serve Script" cmd /k python asyncserve.py

:: Wait for asyncserve to fully boot up (ngrok included)
:: echo Waiting 5 seconds for asyncserve to initialize...
:: timeout /t 5 >nul

:: Get current Unix time in seconds
for /f %%i in ('powershell -command "[int](Get-Date -UFormat %%s)"') do set start_seconds=%%i

:loop
:: Get current Unix time in seconds
for /f %%i in ('powershell -command "[int](Get-Date -UFormat %%s)"') do set now_seconds=%%i

:: Calculate elapsed time
set /a elapsed_seconds=%now_seconds% - %start_seconds%
set /a elapsed_minutes=%elapsed_seconds% / 60
	
:: Check if MAX_RUNTIME_MINUTES have passed
if %elapsed_minutes% GEQ %MAX_RUNTIME_MINUTES% goto end

:: Run asyncscrape.py in a temporary terminal
start "" cmd /c python asyncscrape.py %UI_MODE% %LOOPRANGE% %USER% %HEADLESS%

:: Show time until next scrape
echo [%time%] asyncscrape.py triggered. Waiting %INTERVAL_MINUTES% minutes until next run...
timeout /t %INTERVAL_SECONDS% >nul

goto loop

:end
:: Kill Serve Script terminal
taskkill /FI "WINDOWTITLE eq Serve Script*" /T /F

echo All tasks ended after %MAX_RUNTIME_MINUTES% minutes.
exit /b
