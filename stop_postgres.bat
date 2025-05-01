@echo off
REM Navigate to the infra folder
cd /d "C:\Users\Kris\Dropbox\Safe Harbor\AI Projects\edgar-app\infra"

REM Stop the Postgres container
docker compose down

REM Confirm it's stopped
docker ps

pause
