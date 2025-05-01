@echo off
REM Navigate to the infra folder
cd /d "C:\Users\Kris\Dropbox\Safe Harbor\AI Projects\edgar-app\infra"

REM Start the Postgres container
docker compose up -d

REM Confirm the container started
docker ps

pause
