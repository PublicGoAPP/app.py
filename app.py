import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go Elite v72", layout="wide")

# --- 1. CONFIGURACIÓN DE LA FUENTE (GOOGLE SHEETS) ---
# Asegúrate de que el ID sea el correcto y la hoja sea pública (Lector)
SHEET_ID = "1147SVSNiHRlM74tVcn36T2PzMqTPOGulHcEt8AMKUMc" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- 2. ESTILOS VISUALES CORPORATIVOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-tag { padding: 4px 10px; border-radius: 15px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: inline-block; }
    .report-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 6px solid #003b5c; margin-bottom: 25px; box-shadow: 2px 2px 12px rgba(0,0,0,0.06); }
    .noticia-titulo { color: #003b5c; font-weight: bold; font-size: 1.25rem; line-height: 1.3; margin-bottom: 8px; }
    .analisis-texto { color: #333; line-height: 1.6; font-size: 1rem; }
    .fuente-link { color: #003b5c; text-decoration: none; font-weight: 600; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE INDICADORES (SIDEBAR) ---
def obtener_indicadores(alcance):
    tasa_actual = 417.3579
    variaciones = {"Hoy": +0.85, "Semana": +1.20, "Mes": +3.45}
    return tasa_actual, variaciones.get(alcance, 0)

# --- 4. MOTOR DE CARGA DE INTELIGENCIA ---
@st.cache_data(ttl=300) # Se actualiza cada 5 minutos
def cargar_datos_estrategicos():
    try:
        df = pd.read_csv(SHEET_URL)
        # Limpiamos nombres de columnas por si acaso hay espacios
        df.columns = df.columns.str.strip()
        # Mostramos lo más reciente primero
        return df.iloc[::-1]
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# --- 5. INTERFAZ SIDEBAR ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=PUBLIC+GO", use_container_width=True) # Reemplaza con tu logo real
    st.divider()
    alcance = st.radio("Filtro de Entorno:", ["Hoy", "Semana", "Mes"])
    
    tasa, delta = obtener_indicadores(alcance)
    st.metric(label="Tasa Oficial BCV", value=f"{tasa:.4f} Bs", delta=f"{delta}%")
    st.metric("Riesgo País (EMBI)", "18,450 bps", "-50 bps", delta_color="inverse")
    
    st.divider()
    st.write("📊 **Monitor Energético**")
    st.caption("Cesta OPEP: $79.40 (+0.5%)")
    st.caption("Producción PDVSA: 87
