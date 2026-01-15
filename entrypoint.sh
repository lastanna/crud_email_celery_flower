#!/bin/sh

# Остановить выполнение при любой ошибке
set -e

echo "Ожидание запуска базы данных..."
# Ждем, пока БД станет доступна (замените db на имя вашего сервиса БД в compose)
# Это предотвращает ошибку "Connection refused"
until python manage.py shell -c "import django; django.db.connection.ensure_connection()" 2>/dev/null; do
  sleep 1
done

echo "База данных готова. Запуск миграций..."
python manage.py makemigrations
python manage.py migrate
echo "Создание суперпользователя..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpass')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Суперпользователь "{username}" создан.')
else:
    print(f'Суперпользователь "{username}" уже существует.')
EOF

exec "$@"
