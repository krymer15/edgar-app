@echo off
echo Deleting all __pycache__ folders recursively...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo Done!
pause
