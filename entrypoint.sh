#!/bin/sh
set -e

if [ "$RUN_SETUP" = "true" ]; then
    echo "--- MAIN CONTAINER: Running migrations ---"
    python manage.py migrate --noinput

    # Включаем режим WAL для SQLite (улучшает работу с Celery)
    python manage.py shell -c "import sqlite3; conn = sqlite3.connect('db_storage/db.sqlite3'); conn.execute('PRAGMA journal_mode=WAL;')"

    echo "--- MAIN CONTAINER: Checking Superuser ---"
    python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username,
        os.getenv('DJANGO_SUPERUSER_EMAIL'),
        os.getenv('DJANGO_SUPERUSER_PASSWORD')
    )
    print(f'Superuser {username} created.')
EOF
else
    echo "--- WORKER/FLOWER: Waiting for database file ---"
    # Ждем, пока основной контейнер создаст файл базы
    until [ -f "/app/db_storage/db.sqlite3" ]; do
      sleep 2
    done

fi

echo "--- Starting command: $@ ---"
exec "$@"