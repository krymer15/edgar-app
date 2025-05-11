@echo off
echo Searching for and deleting all __pycache__ folders in %cd%...
for /d /r %%i in (__pycache__) do (
    if exist "%%i" (
        echo Deleting folder: %%i
        rmdir /s /q "%%i"
    )
)
echo Done.
pause
