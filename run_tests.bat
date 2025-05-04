@echo off
REM ===============================================
REM Safe Harbor EDGAR AI Platform – Test Runner
REM ===============================================
REM Features:
REM - Recursively runs all test_*.py scripts inside /tests/
REM - Skips any test scripts listed in SKIP_LIST (by filename)
REM - Skips any subfolders listed in SKIP_FOLDERS
REM - Uses `python -m` so relative imports (utils.bootstrap, etc.) work properly
REM - Easy to customize for partial test runs or CI integration
REM ===============================================

setlocal EnableDelayedExpansion
cd /d %~dp0

REM Optional: activate virtualenv
REM call edgar-env\Scripts\activate.bat

echo.
echo === Safe Harbor AI Test Runner ===
echo.

REM List test files to skip (exclude the .py extension)
set SKIP_LIST=test_deprecated test_old_collector

REM List test subfolders to skip (relative to /tests/)
set SKIP_FOLDERS=tests\archived

REM Recursively find all test_*.py files in tests/
for /R %%F in (tests\test_*.py) do (
    set "SKIP=0"

    REM Check if the path starts with any skipped folder
    for %%D in (%SKIP_FOLDERS%) do (
        echo %%~fF | findstr /I /C:"%%~fD" >nul
        if not errorlevel 1 (
            set "SKIP=1"
        )
    )

    REM Check if the file is in the SKIP_LIST
    for %%S in (%SKIP_LIST%) do (
        echo %%~nF | findstr /I /C:"%%S" >nul
        if not errorlevel 1 (
            set "SKIP=1"
        )
    )

    if "!SKIP!"=="0" (
        REM Convert full path to module path for `python -m`
        set "MODULE=%%~pnF"
        set "MODULE=!MODULE:\=.!."
        echo Running: python -m !MODULE!
        python -m !MODULE!
    ) else (
        echo Skipping: %%F
    )
)

echo.
echo === ✅ All requested tests complete ===
pause
endlocal
