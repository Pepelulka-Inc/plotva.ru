FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование общих Python модулей
COPY ./src /app/src
COPY ./pyproject.toml /app/pyproject.toml

# Переходим в директорию сервиса
WORKDIR /app/order_service

# Копирование и установка зависимостей сервиса
COPY order_service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода сервиса
COPY order_service .

# Запуск приложения
ENTRYPOINT ["python", "main.py"]
