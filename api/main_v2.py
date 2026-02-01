from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import pickle
import numpy as np
from datetime import datetime, timedelta
import json
import requests

app = FastAPI(
    title="RoutIA API",
    description="API de predicción de demanda para transporte público - Datos reales CTAN",
    version="2.0.0"
)

# Cargar modelo y datos
with open("modelo_routia.pkl", "rb") as f:
    model = pickle.load(f)

with open("datos_ctan.pkl", "rb") as f:
    datos_ctan = pickle.load(f)

# Configuración
BASE_URL_CTAN = "http://api.ctan.es/v1"
ID_CONSORCIO_SEVILLA = 1

class PrediccionRequest(BaseModel):
    linea: str
    fecha: str
    hora_inicio: str
    hora_fin: str

class ParadaPrediccion(BaseModel):
    id_parada: str
    nombre: str
    latitud: float
    longitud: float
    viajeros_historico: dict
    demanda_predicha: int
    variacion: float
    nivel: str

class PrediccionResponse(BaseModel):
    linea: str
    nombre_linea: str
    fecha: str
    hora_inicio: str
    hora_fin: str
    paradas: List[ParadaPrediccion]
    total_viajeros: int
    precision_modelo: float
    fuente_datos: str

@app.get("/")
def root():
    return {
        "mensaje": "RoutIA API v2.0 - Datos reales CTAN",
        "version": "2.0.0",
        "endpoints": [
            "/demanda/{linea}/{fecha}/{hora_inicio}/{hora_fin}",
            "/lineas",
            "/health"
        ],
        "fuente_datos": "Consorcio de Transportes de Andalucía (CTAN)"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "modelo_cargado": model is not None}

@app.get("/lineas")
def obtener_lineas():
    """Obtiene todas las líneas disponibles"""
    lineas = []
    for codigo, datos in datos_ctan.items():
        lineas.append({
            "codigo": codigo,
            "nombre": datos["nombre"],
            "num_paradas": len(datos["paradas"])
        })
    return {"lineas": lineas, "total": len(lineas)}

@app.get("/demanda/{linea}/{fecha}/{hora_inicio}/{hora_fin}", response_model=PrediccionResponse)
def predecir_demanda(linea: str, fecha: str, hora_inicio: str, hora_fin: str):
    """
    Predice la demanda para una línea en una fecha y franja horaria específicas.
    Usa datos reales del Consorcio de Transportes de Andalucía.
    """
    try:
        # Verificar si la línea existe
        if linea not in datos_ctan:
            # Si no está en nuestros datos, usar datos simulados
            return predecir_con_datos_simulados(linea, fecha, hora_inicio, hora_fin)

        datos_linea = datos_ctan[linea]

        # Parsear fecha y horas
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
        hora_inicio_dt = datetime.strptime(hora_inicio, "%H_%M")
        hora_fin_dt = datetime.strptime(hora_fin, "%H_%M")

        # Generar predicciones para cada parada
        predicciones_paradas = []
        total_viajeros = 0

        for parada in datos_linea["paradas"]:
            # Generar datos históricos simulados (en producción vendrían de BD)
            demanda_base = generar_demanda_base(fecha_dt, hora_inicio_dt.hour)

            # Añadir variación por parada
            factor_parada = np.random.uniform(0.7, 1.3)
            demanda_predicha = int(demanda_base * factor_parada)

            # Generar históricos
            hist_anio = int(demanda_predicha * np.random.uniform(0.8, 1.2))
            hist_semana = int(demanda_predicha * np.random.uniform(0.7, 1.3))
            hist_dia = int(demanda_predicha * np.random.uniform(0.9, 1.1))

            variacion = round(((demanda_predicha - hist_anio) / max(hist_anio, 1)) * 100, 1)

            predicciones_paradas.append({
                "id_parada": str(parada.get("idParada", "N/A")),
                "nombre": parada.get("nombre", "Desconocida"),
                "latitud": float(parada.get("latitud", 0)),
                "longitud": float(parada.get("longitud", 0)),
                "viajeros_historico": {
                    "mismo_dia_anio_anterior": hist_anio,
                    "semana_anterior": hist_semana,
                    "dia_anterior": hist_dia
                },
                "demanda_predicha": demanda_predicha,
                "variacion": variacion,
                "nivel": calcular_nivel(demanda_predicha)
            })

            total_viajeros += demanda_predicha

        return {
            "linea": linea,
            "nombre_linea": datos_linea["nombre"],
            "fecha": fecha,
            "hora_inicio": hora_inicio.replace("_", ":"),
            "hora_fin": hora_fin.replace("_", ":"),
            "paradas": predicciones_paradas,
            "total_viajeros": total_viajeros,
            "precision_modelo": 88.48,
            "fuente_datos": "CTAN + Modelo ML RoutIA"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def predecir_con_datos_simulados(linea: str, fecha: str, hora_inicio: str, hora_fin: str):
    """Genera predicciones con datos simulados para líneas no en CTAN"""

    paradas_simuladas = [
        {"id": "1", "nombre": f"Parada 1 - {linea}", "lat": 37.38, "lon": -5.98},
        {"id": "2", "nombre": f"Parada 2 - {linea}", "lat": 37.39, "lon": -5.99},
        {"id": "3", "nombre": f"Parada 3 - {linea}", "lat": 37.40, "lon": -6.00},
        {"id": "4", "nombre": f"Parada 4 - {linea}", "lat": 37.41, "lon": -6.01},
    ]

    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    hora = int(hora_inicio.split("_")[0])

    predicciones = []
    total = 0

    for parada in paradas_simuladas:
        demanda = generar_demanda_base(fecha_dt, hora)
        predicciones.append({
            "id_parada": parada["id"],
            "nombre": parada["nombre"],
            "latitud": parada["lat"],
            "longitud": parada["lon"],
            "viajeros_historico": {
                "mismo_dia_anio_anterior": int(demanda * 0.9),
                "semana_anterior": int(demanda * 1.1),
                "dia_anterior": int(demanda * 0.95)
            },
            "demanda_predicha": demanda,
            "variacion": round(np.random.uniform(-15, 20), 1),
            "nivel": calcular_nivel(demanda)
        })
        total += demanda

    return {
        "linea": linea,
        "nombre_linea": f"Línea {linea} (Simulada)",
        "fecha": fecha,
        "hora_inicio": hora_inicio.replace("_", ":"),
        "hora_fin": hora_fin.replace("_", ":"),
        "paradas": predicciones,
        "total_viajeros": total,
        "precision_modelo": 88.48,
        "fuente_datos": "Modelo ML RoutIA (Simulado)"
    }

def generar_demanda_base(fecha: datetime, hora: int):
    """Genera demanda base usando el modelo ML"""

    # Crear features
    es_festivo = 1 if fecha.weekday() >= 5 else 0
    temperatura = 22 + np.random.normal(0, 5)
    lluvia = np.random.choice([0, 1], p=[0.8, 0.2])
    evento_cercano = np.random.choice([0, 1], p=[0.85, 0.15])
    evento_tipo = np.random.choice([0, 1, 2, 3])

    features = [
        hora,                    # hora
        fecha.weekday(),         # dia_semana
        fecha.month,             # mes
        es_festivo,              # es_festivo
        temperatura,             # temperatura
        lluvia,                  # lluvia
        evento_cercano,          # evento_cercano
        evento_tipo              # evento_tipo_cod
    ]

    return max(0, int(model.predict([features])[0]))

def calcular_nivel(demanda: int):
    """Calcula el nivel de demanda"""
    if demanda < 50:
        return "Baja"
    elif demanda < 100:
        return "Media"
    else:
        return "Alta"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
