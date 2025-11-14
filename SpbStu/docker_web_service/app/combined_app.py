import subprocess
import time
from threading import Thread
import sys


def run_fastapi():
    """Запуск FastAPI сервера"""
    print("🚀 Запуск FastAPI сервера на порту 8000...")
    subprocess.run(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd="/app"
    )


def run_flask():
    """Запуск Flask сервера"""
    print("⏳ Ожидание запуска FastAPI...")
    time.sleep(5)  # Ждем 5 секунд пока FastAPI запустится
    print("🚀 Запуск Flask сервера на порту 5000...")
    subprocess.run(["python", "app/flask_app.py"], cwd="/app")


if __name__ == "__main__":
    print("=" * 50)
    print("Запуск ML Web Service (Flask + FastAPI)")
    print("=" * 50)

    # Создаем два потока для параллельного запуска сервисов
    fastapi_thread = Thread(target=run_fastapi, daemon=False)
    flask_thread = Thread(target=run_flask, daemon=False)

    # Запускаем оба потока
    fastapi_thread.start()
    flask_thread.start()

    try:
        # Держим главный процесс живым
        fastapi_thread.join()
        flask_thread.join()
    except KeyboardInterrupt:
        print("\n⛔ Остановка сервисов...")
        sys.exit(0)
