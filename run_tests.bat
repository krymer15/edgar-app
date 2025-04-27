@echo off
REM Navigate to the project root if not already there
cd /d %~dp0

REM Set environment for better output
echo Running all unit tests in the /tests folder...
echo.

REM Activate your environment if needed (optional - comment out if using manually)
REM call conda activate edgar-env

REM Run unittest discovery inside tests/
python -m unittest discover -s tests -p "test_*.py" -v

echo.
echo All tests completed.
pause
