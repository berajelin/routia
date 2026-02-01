import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json

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

# Titulo
st.title("🚌 RoutIA - Dashboard de Predicciones")
st.markdown("### Prediccion Inteligente de Demanda para Transporte Publico")

# Sidebar
st.sidebar.header("Configuracion")

# Selector de linea
lineas_disponibles = ["L41", "L32", "C2", "L15", "L27", "L03"]
linea = st.sidebar.selectbox("Selecciona linea:", lineas_disponibles)

# Selector de fecha
fecha = st.sidebar.date_input("Fecha:", date.today())

# Selector de horario
col1, col2 = st.sidebar.columns(2)
with col1:
    hora_inicio = st.time_input("Hora inicio:", datetime.strptime("08:00", "%H:%M").time())
with col2:
    hora_fin = st.time_input("Hora fin:", datetime.strptime("09:00", "%H:%M").time())

# Boton de prediccion
if st.sidebar.button("🔮 Predecir Demanda", use_container_width=True):
    # Formatear parametros
    fecha_str = fecha.strftime("%Y-%m-%d")
    hora_inicio_str = hora_inicio.strftime("%H_%M")
    hora_fin_str = hora_fin.strftime("%H_%M")
    
    # Llamar a la API
    try:
        api_url = f"http://localhost:8000/demanda/{linea}/{fecha_str}/{hora_inicio_str}/{hora_fin_str}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Metricas principales
            st.markdown("---")
            st.subheader(f"Prediccion para Linea {data['linea']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Viajeros", f"{data['total_viajeros']:,}")
            with col2:
                st.metric("Precision Modelo", f"{data['precision_modelo']}%")
            with col3:
                st.metric("Paradas", len(data['paradas']))
            
            # Grafico de barras
            if data['paradas']:
                df = pd.DataFrame(data['paradas'])
                
                fig = px.bar(
                    df,
                    x='nombre',
                    y='demanda_predicha',
                    title=f"Demanda por Parada - Linea {linea}",
                    color='nivel',
                    color_discrete_map={
                        'Alta': '#ff6b6b',
                        'Media': '#ffd93d',
                        'Baja': '#6bcf7f'
                    }
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabla de datos
                st.subheader("Detalle por Parada")
                st.dataframe(df, use_container_width=True)
        else:
            st.error(f"Error al consultar la API: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.warning("No se pudo conectar con la API. Asegurate de que esta ejecutandose en localhost:8000")
    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    # Estado inicial
    st.info("👈 Configura los parametros en el panel lateral y haz clic en 'Predecir Demanda'")
    
    # Info del proyecto
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Sobre RoutIA
        Sistema de prediccion de demanda para transporte publico
        basado en Machine Learning con datos reales del CTAN.
        
        **Precision del modelo:** 88.48%
        """)
    with col2:
        st.markdown("""
        ### Tecnologias
        - FastAPI + scikit-learn
        - Datos reales CTAN
        - Gradient Boosting
        - 8 variables predictivas
        """)
