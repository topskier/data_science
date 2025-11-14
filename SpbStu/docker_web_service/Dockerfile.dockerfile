# Используем официальный образ Python версии 3.10 с минимальным размером
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Обновляем систему и устанавливаем системные зависимости
# которые могут потребоваться для некоторых Python пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip и устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое директории app в контейнер
COPY ./app /app/app

# Копируем директорию с моделями
COPY ./models /app/models

# Создаём непривилегированного пользователя для безопасности
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Переходим на непривилегированного пользователя
USER appuser

# Открываем порт 8000 (этот порт будет слушать FastAPI)
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
