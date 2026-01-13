# Use a modern, stable Python base image (Python 3.12+ recommended for 2026)
FROM python:3.12-slim

# Для оптимизации производительности питона задаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую папку
WORKDIR /app
# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . .

# Создаем пользователя для безопасности, чтобы не использовать рут
RUN adduser --disabled-password --no-create-home appuser
USER appuser
RUN cd /app
# порт для Daphne еще не реализовано
EXPOSE 8000

# Команда для запуска django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
