# RoutIA

Predicción Inteligente de Demanda para Transporte Público

## Descripción

RoutIA transforma la gestión del transporte público de reactiva a predictiva utilizando Inteligencia Artificial y datos reales del Consorcio de Transportes de Andalucía (CTAN).

## Características

- **Modelo ML** con 88,48% de precisión en predicciones
- **API REST** con FastAPI y datos reales CTAN
- **Dashboard** interactivo con Streamlit
- **8 variables** predictivas (hora, día, clima, eventos)
- **5.000 registros** históricos

## Tecnologías

- **Backend:** FastAPI, Python
- **ML:** scikit-learn, Gradient Boosting
- **Datos:** CTAN API, AEMET
- **Dashboard:** Streamlit
- **Deploy:** Docker, AWS

## Estructura

```
routia/
├── index.html       # Web estática
├── hero-bg.jpg      # Imagen de fondo
├── api/             # API REST + Dashboard
│   ├── main_v2.py   # API principal (v2 con CTAN)
│   ├── main.py      # API v1
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── docs/            # Documentación
│   ├── CDO_Documento_Completo.md
│   └── RoutIA_Playbook.md
└── README.md        # Este archivo
```

## Quick Start

```bash
cd api
pip install -r requirements.txt
python main_v2.py
```

## Documentación

- [Documento CDO](docs/CDO_Documento_Completo.md)
- [Playbook Empresa](docs/RoutIA_Playbook.md)
- [API Docs](api/README.md)

## Equipo

- **CDO:** Berajelin Gaitan
- **CEO:** María López Torres
- **CTO:** David Ruiz Fernández
- **CFO:** Álvaro García Solís

## Proyecto Académico

EOI Sevilla - Máster en IA y Big Data 2025-2026

## Web

🌐 [https://berajelin.github.io/routia](https://berajelin.github.io/routia)# routia
RoutIA - Predicción Inteligente para Transporte Público
