@echo off
REM Set timestamp
set timestamp=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set timestamp=%timestamp: =0%

REM Output path on SSD
set backup_dir=D:\safeharbor-postgres\backups
set backup_file=%backup_dir%\edgar_app_db_backup_%timestamp%.sql

REM Create backup directory if missing
if not exist %backup_dir% (
    mkdir %backup_dir%
)

REM Run pg_dump inside container
docker exec ai_agent_postgres pg_dump -U myuser -d myagentdb -f /tmp/backup.sql

REM Copy from container to host
docker cp ai_agent_postgres:/tmp/backup.sql "%backup_file%"

REM Clean up temp file in container
docker exec ai_agent_postgres rm /tmp/backup.sql

echo Backup completed: %backup_file%
pause
