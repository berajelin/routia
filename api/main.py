from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pickle
import numpy as np
from datetime import datetime, timedelta
import json

app = FastAPI(
    title="RoutIA API",
    description="API de predicción de demanda para transporte público",
    version="1.0.0"
)

# Cargar modelo
with open("modelo_routia.pkl", "rb") as f:
    model = pickle.load(f)

# Features del modelo
FEATURES = ['hora', 'dia_semana', 'mes', 'es_festivo', 'temperatura',
            'lluvia', 'evento_cercano', 'evento_tipo_cod']

class PrediccionRequest(BaseModel):
    linea: str
    fecha: str  # formato: YYYY-MM-DD
    hora_inicio: str  # formato: HH:MM
    hora_fin: str  # formato: HH:MM

class PrediccionResponse(BaseModel):
    linea: str
    fecha: str
    hora_inicio: str
    hora_fin: str
    paradas: list
    total_viajeros: int
    precision_modelo: float

@app.get("/")
def root():
    return {
        "mensaje": "Bienvenido a RoutIA API",
        "version": "1.0.0",
        "endpoints": [
            "/demanda/{linea}/{fecha}/{hora_inicio}/{hora_fin}"
        ]
    }

@app.get("/demanda/{linea}/{fecha}/{hora_inicio}/{hora_fin}")
def predecir_demanda(linea: str, fecha: str, hora_inicio: str, hora_fin: str):
    """
    Predice la demanda para una línea en una fecha y franja horaria específicas.
    """
    try:
        # Parsear fecha
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
        hora = int(hora_inicio.split("_")[0])

        # Generar predicciones simuladas (en producción usaría el modelo real)
        paradas = [
            {"id": 1, "nombre": f"Parada 1 - {linea}", "demanda": 85},
            {"id": 2, "nombre": f"Parada 2 - {linea}", "demanda": 120},
            {"id": 3, "nombre": f"Parada 3 - {linea}", "demanda": 95},
            {"id": 4, "nombre": f"Parada 4 - {linea}", "demanda": 70},
        ]

        total = sum(p["demanda"] for p in paradas)

        return {
            "linea": linea,
            "fecha": fecha,
            "hora_inicio": hora_inicio.replace("_", ":"),
            "hora_fin": hora_fin.replace("_", ":"),
            "paradas": paradas,
            "total_viajeros": total,
            "precision_modelo": 88.48
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
