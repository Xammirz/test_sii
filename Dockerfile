# Установка базового образа
FROM python:3.9-slim-buster

# Установка рабочей директории в контейнере
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование файлов проекта в контейнер
COPY . .

# Команда для запуска приложения
CMD ["python", "main.py"]
