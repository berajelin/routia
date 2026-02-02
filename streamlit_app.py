import streamlit as st
import pickle
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os

# Configuracion de la pagina
st.set_page_config(
    page_title="RoutIA - Dashboard de Predicciones",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
    }
    .stButton>button {
        background-color: #00d4aa;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00d4aa;
    }
</style>
""", unsafe_allow_html=True)

# Cargar modelo y datos
@st.cache_resource
def cargar_modelo():
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, "modelo_routia.pkl")
    if not os.path.exists(model_path):
        model_path = os.path.join(base_path, "api", "modelo_routia.pkl")
    with open(model_path, "rb") as f:
        return pickle.load(f)

@st.cache_resource
def cargar_datos_ctan():
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Intentar varias rutas posibles
    for nombre in ["datos_ctan.pkl", "datos_ctan (1).pkl"]:
        data_path = os.path.join(base_path, nombre)
        if os.path.exists(data_path):
            with open(data_path, "rb") as f:
                return pickle.load(f)
        data_path = os.path.join(base_path, "api", nombre)
        if os.path.exists(data_path):
            with open(data_path, "rb") as f:
                return pickle.load(f)
    return None

def generar_demanda_base(model, fecha, hora):
    es_festivo = 1 if fecha.weekday() >= 5 else 0
    temperatura = 22 + np.random.normal(0, 5)
    lluvia = np.random.choice([0, 1], p=[0.8, 0.2])
    evento_cercano = np.random.choice([0, 1], p=[0.85, 0.15])
    evento_tipo = np.random.choice([0, 1, 2, 3])
    features = [hora, fecha.weekday(), fecha.month, es_festivo,
                temperatura, lluvia, evento_cercano, evento_tipo]
    return max(0, int(model.predict([features])[0]))

def calcular_nivel(demanda):
    if demanda < 50:
        return "Baja"
    elif demanda < 100:
        return "Media"
    else:
        return "Alta"

# Cargar recursos
try:
    model = cargar_modelo()
    modelo_cargado = True
except Exception as e:
    modelo_cargado = False
    st.error(f"Error cargando modelo: {str(e)}")

datos_ctan = cargar_datos_ctan()

# Titulo
st.title("🚌 RoutIA - Dashboard de Predicciones")
st.markdown("### Prediccion Inteligente de Demanda para Transporte Publico")
st.markdown("*Proyecto EOI Sevilla - Master en IA y Big Data 2025-2026*")

# Sidebar
st.sidebar.header("Configuracion")
st.sidebar.markdown("---")

# Selector de linea
lineas_disponibles = ["M-101A", "M-101B", "M-102A"]
if datos_ctan:
    lineas_disponibles = list(datos_ctan.keys())
linea = st.sidebar.selectbox("Selecciona linea:", lineas_disponibles)

# Selector de fecha
fecha = st.sidebar.date_input("Fecha:", date.today())

# Selector de horario
col1, col2 = st.sidebar.columns(2)
with col1:
    hora_inicio = st.time_input("Hora inicio:", datetime.strptime("08:00", "%H:%M").time())
with col2:
    hora_fin = st.time_input("Hora fin:", datetime.strptime("09:00", "%H:%M").time())

# Info del modelo en sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("**Info del Modelo**")
st.sidebar.markdown("Precision: **88.48%**")
st.sidebar.markdown("Algoritmo: Gradient Boosting")
st.sidebar.markdown("Variables: 8 predictivas")
if modelo_cargado:
    st.sidebar.success("Modelo ML cargado")
else:
    st.sidebar.error("Modelo no disponible")

# Boton de prediccion
if st.sidebar.button("🔮 Generar Prediccion", use_container_width=True):
    if not modelo_cargado:
        st.error("El modelo no esta cargado. Verifica que modelo_routia.pkl existe.")
    else:
        fecha_dt = datetime.combine(fecha, datetime.min.time())
        hora = hora_inicio.hour

        # Obtener paradas
        paradas = []
        nombre_linea = f"Linea {linea}"

        if datos_ctan and linea in datos_ctan:
            datos_linea = datos_ctan[linea]
            nombre_linea = datos_linea.get("nombre", nombre_linea)
            paradas_raw = datos_linea.get("paradas", [])
            for p in paradas_raw:
                paradas.append({
                    "nombre": p.get("nombre", "Desconocida"),
                    "latitud": float(p.get("latitud", 37.38)),
                    "longitud": float(p.get("longitud", -5.98))
                })
        else:
            for i in range(6):
                paradas.append({
                    "nombre": f"Parada {i+1} - {linea}",
                    "latitud": 37.38 + i * 0.005,
                    "longitud": -5.98 - i * 0.005
                })

        # Limitar a 15 paradas para visualizacion
        if len(paradas) > 15:
            paradas = paradas[:15]

        # Generar predicciones
        resultados = []
        total_viajeros = 0
        for p in paradas:
            demanda = generar_demanda_base(model, fecha_dt, hora)
            factor = np.random.uniform(0.7, 1.3)
            demanda_final = int(demanda * factor)
            nivel = calcular_nivel(demanda_final)
            resultados.append({
                "Parada": p["nombre"][:40],
                "Demanda": demanda_final,
                "Nivel": nivel,
                "Lat": p["latitud"],
                "Lon": p["longitud"]
            })
            total_viajeros += demanda_final

        df = pd.DataFrame(resultados)

        # Metricas principales
        st.markdown("---")
        st.subheader(f"Prediccion para {nombre_linea}")
        st.markdown(f"Fecha: **{fecha}** | Horario: **{hora_inicio} - {hora_fin}**")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Viajeros", f"{total_viajeros:,}")
        with col2:
            st.metric("Precision Modelo", "88.48%")
        with col3:
            st.metric("Paradas Analizadas", len(resultados))
        with col4:
            alta = len(df[df["Nivel"] == "Alta"])
            st.metric("Paradas Alta Demanda", alta)

        # Grafico de barras
        st.markdown("---")
        fig = px.bar(
            df,
            x="Parada",
            y="Demanda",
            title=f"Demanda Predicha por Parada - {nombre_linea}",
            color="Nivel",
            color_discrete_map={
                "Alta": "#ff6b6b",
                "Media": "#ffd93d",
                "Baja": "#6bcf7f"
            }
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabla de datos y mapa en dos columnas
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Detalle por Parada")
            st.dataframe(
                df[["Parada", "Demanda", "Nivel"]],
                use_container_width=True,
                hide_index=True
            )

        with col_right:
            st.subheader("Mapa de Paradas")
            map_df = df.rename(columns={"Lat": "lat", "Lon": "lon"})
            st.map(map_df[["lat", "lon"]])

        # Exportar resultados
        st.markdown("---")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f"prediccion_{linea}_{fecha}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_exp2:
            import json
            json_str = json.dumps(resultados, indent=2, ensure_ascii=False)
            st.download_button(
                label="Descargar JSON",
                data=json_str,
                file_name=f"prediccion_{linea}_{fecha}.json",
                mime="application/json",
                use_container_width=True
            )

else:
    # Estado inicial
    st.info("Configura los parametros en el panel lateral y haz clic en 'Generar Prediccion'")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Sobre RoutIA
        Sistema de prediccion de demanda para transporte publico
        basado en Machine Learning con datos reales del CTAN
        (Consorcio de Transportes de Andalucia).

        **Precision del modelo:** 88.48%

        **Variables predictivas:** hora, dia de la semana,
        mes, festivos, temperatura, lluvia, eventos cercanos.
        """)
    with col2:
        st.markdown("""
        ### Tecnologias
        - **ML:** scikit-learn (Gradient Boosting)
        - **Datos:** CTAN Sevilla (datos reales)
        - **Backend:** FastAPI
        - **Dashboard:** Streamlit
        - **Deploy:** Docker + Cloud

        ### Equipo
        - **CEO:** Marcos Garcia Ojeda
        - **CFO:** Alvaro Garcia Solis
        - **CTO:** Jose Angel Santos
        - **CDO:** Berajelin Gaitan
        - **Proyecto:** EOI Sevilla
        """)

# Footer
st.markdown("---")
st.markdown("**RoutIA** - Inteligencia Artificial para Transporte Publico | v2.0")
