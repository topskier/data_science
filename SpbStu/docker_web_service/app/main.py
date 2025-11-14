from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(
    title="Insurance Claim Prediction Service",
    description="API для предсказания вероятности убытка",
    version="1.0.0",
)


class PredictionRequest(BaseModel):
    Second_driver: int
    Year_matriculation: int
    Power: float
    Age: int
    Driving_experience: int


class PredictionResponse(BaseModel):
    claim_prob: float


model = None


@app.on_event("startup")
def load_model():
    global model
    try:
        model = joblib.load("models/my_XGB.pkl")
        print("✓ Модель успешно загружена")
    except Exception as e:
        print(f"❌ Ошибка при загрузке модели: {e}")


@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    try:
        features = np.array(
            [
                [
                    req.Second_driver,
                    req.Year_matriculation,
                    req.Power,
                    req.Age,
                    req.Driving_experience,
                ]
            ]
        )

        if model is not None:
            claim_prob = float(model.predict_proba(features)[0][1])
        else:
            claim_prob = float(np.mean(features))

        return PredictionResponse(claim_prob=round(claim_prob, 4))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {e}")


@app.get("/")
def root():
    return {"message": "Insurance API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}
