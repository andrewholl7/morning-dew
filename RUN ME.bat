@echo off
cd /d "%~dp0"
python "a.Context and Documentation\main.py"
if errorlevel 1 (
    echo.
    echo Something went wrong -- see error above.
    pause
) else (
    start "" "Live Site.html"
)
