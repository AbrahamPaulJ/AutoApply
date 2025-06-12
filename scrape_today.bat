setlocal

set UI_MODE=1
set LOOPRANGE=5
set USER=abraham
set HEADLESS=0
set FIRST_RUN=1  :: New flag

:: Time limit in minutes
set MAX_RUNTIME_MINUTES=600
set INTERVAL_MINUTES=5
set /a INTERVAL_SECONDS=%INTERVAL_MINUTES% * 60

:loop
:: Get current Unix time in seconds
for /f %%i in ('powershell -command "[int](Get-Date -UFormat %%s)"') do set now_seconds=%%i

:: Calculate elapsed time
set /a elapsed_seconds=%now_seconds% - %start_seconds%
set /a elapsed_minutes=%elapsed_seconds% / 60

:: Check if MAX_RUNTIME_MINUTES have passed
if %elapsed_minutes% GEQ %MAX_RUNTIME_MINUTES% goto end

:: Run asyncscrape.py
start "" cmd /c python asyncscrape.py %UI_MODE% %LOOPRANGE% %USER% %HEADLESS%

:: Reset UI_MODE to 0 after first run
if %FIRST_RUN%==1 (
    set UI_MODE=0
    set FIRST_RUN=0
)

:: Show time until next scrape
echo [%time%] asyncscrape.py triggered. Waiting %INTERVAL_MINUTES% minutes until next run...
timeout /t %INTERVAL_SECONDS% >nul

goto loop