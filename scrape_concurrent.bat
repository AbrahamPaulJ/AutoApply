@echo off
setlocal

set LOOPRANGE=1
set TIMEFRAME=\\d{1,2}m
set USER=abraham_paul_jaison
set TOGGLE=0

:: Time limit in minutes
set MAX_RUNTIME_MINUTES=600
set INTERVAL_MINUTES=2
set /a INTERVAL_SECONDS=%INTERVAL_MINUTES% * 60

:: Start asyncserve.py in a new terminal
start "Serve Script" cmd /k python asyncserve.py

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

:: Alternate USER
if %TOGGLE%==0 (
    set USER=abraham_paul_jaison
    set TOGGLE=1
) else (
    set USER=Me
    set TOGGLE=0
)

:: Run asyncscrape.py in a temporary terminal
start "" cmd /c python asyncscrape.py %LOOPRANGE% %TIMEFRAME% %USER%

:: Show time until next scrape
echo [%time%] asyncscrape.py triggered for user: %USER%. Waiting %INTERVAL_MINUTES% minutes until next run...
timeout /t %INTERVAL_SECONDS% >nul

goto loop

:end
:: Kill Serve Script terminal
taskkill /FI "WINDOWTITLE eq Serve Script*" /T /F

echo All tasks ended after %MAX_RUNTIME_MINUTES% minutes.
exit /b
