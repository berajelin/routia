# RoutIA API

API REST para predicción de demanda de transporte público.

## Endpoints

### GET /demanda/{linea}/{fecha}/{hora_inicio}/{hora_fin}

Predice la demanda para una línea.

**Ejemplo:** RoutIA API

API REST para predicción de demanda de transporte público.

## Endpoints

### GET /demanda/{linea}/{fecha}/{hora_inicio}/{hora_fin}

Predice la demanda para una línea en una fecha y franja horaria.

**Parámetros:**
- `linea`: Código de la línea (L41, L32, C2, L15)
- - `fecha`: Fecha en formato YYYY-MM-DD
  - - `hora_inicio`: Hora de inicio en formato HH_MM
    - - `hora_fin`: Hora de fin en formato HH_MM
     
      - **Ejemplo:**
     
      - ```
        GET /demanda/L41/2026-01-08/8_30/9_00
        ```

        ### GET /lineas

        Lista todas las líneas disponibles.

        ### GET /health

        Estado de la API.

        ## Ejecutar localmente

        ```bash
        pip install -r requirements.txt
        python main_v2.py
        ```

        ## Docker

        ```bash
        docker build -t routia-api .
        docker run -p 8000:8000 routia-api
        ```

        ## Tecnologías

        - FastAPI
        - - scikit-learn
          - - Datos reales CTAN (Consorcio de Transportes de Andalucía)
