from flask import Flask, render_template, request, jsonify
import requests
import os
import time

app = Flask(__name__, template_folder="templates", static_folder="static")

# URL FastAPI сервиса - используем localhost так как они в одном контейнере
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# Переменная для отслеживания готовности FastAPI
MAX_RETRIES = 10
RETRY_DELAY = 1


def wait_for_fastapi():
    """Ожидание пока FastAPI станет доступным"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(f"{FASTAPI_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"✓ FastAPI доступен!")
                return True
        except requests.exceptions.RequestException:
            print(f"⏳ Попытка {attempt + 1}/{MAX_RETRIES}: ожидание FastAPI...")
            time.sleep(RETRY_DELAY)
    return False


@app.route("/")
def index():
    """Главная страница с формой"""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """Обработка запроса от формы и отправка в FastAPI"""
    try:
        # Получаем данные из формы
        data = {
            "Second_driver": int(request.form["second_driver"]),
            "Year_matriculation": int(request.form["year_matriculation"]),
            "Power": float(request.form["power"]),
            "Age": int(request.form["age"]),
            "Driving_experience": int(request.form["driving_experience"]),
        }

        print(f"📝 Запрос с данными: {data}")

        # Отправляем запрос к FastAPI
        response = requests.post(f"{FASTAPI_URL}/predict", json=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            claim_prob = result["claim_prob"]
            print(f"✓ Предсказание получено: {claim_prob}")

            return jsonify(
                {
                    "success": True,
                    "claim_prob": claim_prob,
                    "message": f"Вероятность наступления убытка: {claim_prob:.4f}",
                }
            )
        else:
            error_msg = f"Ошибка сервера: {response.status_code}"
            print(f"❌ {error_msg}")
            return jsonify({"success": False, "message": error_msg}), 500

    except ValueError as e:
        error_msg = f"Ошибка валидации данных: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({"success": False, "message": error_msg}), 400
    except requests.exceptions.ConnectionError:
        error_msg = "Ошибка соединения с FastAPI сервером"
        print(f"❌ {error_msg}")
        return jsonify({"success": False, "message": error_msg}), 500
    except Exception as e:
        error_msg = f"Произошла ошибка: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({"success": False, "message": error_msg}), 500


@app.route("/health")
def health():
    """Проверка здоровья Flask сервиса"""
    return jsonify({"status": "healthy", "service": "flask"})


if __name__ == "__main__":
    print("=" * 50)
    print("Flask Web Interface Starting")
    print("=" * 50)

    # Ожидаем пока FastAPI будет готов
    if not wait_for_fastapi():
        print("⚠️  FastAPI недоступен, но Flask запустится")

    # Запускаем Flask
    app.run(host="0.0.0.0", port=5000, debug=False)
