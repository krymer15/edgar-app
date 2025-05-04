@echo off
REM ===============================================
REM Safe Harbor EDGAR AI Platform – Test Runner
REM Project Root: edgar-app/
REM ===============================================
REM Features:
REM - Recursively runs all test_*.py scripts under /tests/
REM - Skips individual test scripts listed in SKIP_LIST (no .py extension)
REM - Skips folders listed in SKIP_FOLDERS (e.g., tests\archived)
REM - Uses `python -m` to maintain correct relative import paths
REM ===============================================

setlocal EnableDelayedExpansion

REM Navigate to the root of edgar-app/ (this .bat file must live there)
cd /d %~dp0

REM Optional: activate virtual environment (edit this if your venv folder differs)
REM call edgar-env\Scripts\activate.bat

echo.
echo === 🚀 Running Tests in edgar-app/tests ===
echo.

REM List test files (by filename without extension) to skip
set SKIP_LIST=test_deprecated test_old_collector

REM List folders to skip (relative to /tests/)
set SKIP_FOLDERS=tests\archived

REM Recursively run tests matching test_*.py
for /R %%F in (tests\test_*.py) do (
    set "SKIP=0"

    REM Skip folders in SKIP_FOLDERS
    for %%D in (%SKIP_FOLDERS%) do (
        echo %%~fF | findstr /I /C:"%%~fD" >nul
        if not errorlevel 1 (
            set "SKIP=1"
        )
    )

    REM Skip specific files in SKIP_LIST
    for %%S in (%SKIP_LIST%) do (
        echo %%~nF | findstr /I /C:"%%S" >nul
        if not errorlevel 1 (
            set "SKIP=1"
        )
    )

    if "!SKIP!"=="0" (
        REM Convert file path to Python module path (slashes → dots)
        set "MODULE=%%~pnF"
        set "MODULE=!MODULE:\=.!."
        echo Running: python -m !MODULE!
        python -m !MODULE!
    ) else (
        echo Skipping: %%F
    )
)

echo.
echo === ✅ Test run complete ===
pause
endlocal
