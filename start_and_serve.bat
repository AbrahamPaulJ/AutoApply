@echo off
setlocal

:: Time limit in minutes
set MAX_RUNTIME_MINUTES=60
set INTERVAL_MINUTES=2


set /a INTERVAL_SECONDS=%INTERVAL_MINUTES% * 60

:: Get current time in seconds
for /f "tokens=1-4 delims=:.," %%a in ("%time%") do (
    set /a "start_seconds=(((1%%a %% 100)*60 + 1%%b %% 100)*60 + 1%%c %% 100)"
)

:: Start asyncserve.py in a separate window
start "Serve Script" cmd /k python asyncserve.py

:: Wait for asyncserve to fully boot up (ngrok included)
echo Waiting 5 seconds for asyncserve to initialize...
timeout /t 5 >nul

:loop
:: Get current time
for /f "tokens=1-4 delims=:.," %%a in ("%time%") do (
    set /a "now_seconds=(((1%%a %% 100)*60 + 1%%b %% 100)*60 + 1%%c %% 100)"
)

:: Calculate elapsed time
set /a elapsed_seconds=%now_seconds% - %start_seconds%
set /a elapsed_minutes=%elapsed_seconds% / 60

:: Check if 60 minutes have passed
if %elapsed_minutes% GEQ %MAX_RUNTIME_MINUTES% goto end

:: Run asyncscrape.py in a separate temporary terminal
start "" cmd /c python asyncscrape.py

:: Show time until next scrape
echo [%time%] asyncscrape.py triggered. Waiting %INTERVAL_MINUTES% minutes until next run...
timeout /t %INTERVAL_SECONDS%

goto loop

:end
:: Kill all cmd windows with Serve Script
taskkill /FI "WINDOWTITLE eq Serve Script*" /T /F

echo All tasks ended after %MAX_RUNTIME_MINUTES% minutes.
exit /b
