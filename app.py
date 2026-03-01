import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go Elite v71", layout="wide")

# --- 1. CONFIGURACIÓN DE LA FUENTE (PUENTE CON PABBLY) ---
# Reemplaza con el ID de tu Google Sheet que configuramos en Pabbly
SHEET_ID = "TU_ID_DE_GOOGLE_SHEET_AQUI" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- 2. ESTILOS VISUALES ORIGINALES ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .analysis-box { background-color: #f8f9fa; padding: 18px; border-right: 5px solid #003b5c; border-radius: 5px; font-size: 0.95rem; line-height: 1.5; color: #333; margin-bottom: 20px; }
    .news-item { border-bottom: 1px solid #f0f0f0; padding: 12px 0; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: 500; font-size: 1.05rem; }
    .ref-tag { color: #003b5c; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE VARIACIÓN (SIDEBAR) ---
def calcular_variacion_real(alcance):
    tasa_actual = 417.3579
    cierres = {"Hoy": 414.0594, "Semana": 412.2030, "Mes": 401.3055}
    precio_previo = cierres.get(alcance)
    variacion_pct = ((tasa_actual - precio_previo) / precio_previo) * 100
    return tasa_actual, variacion_pct

# --- 4. CARGA DE DATOS DESDE GOOGLE SHEETS ---
@st.cache_data(ttl=300) # Se actualiza cada 5 minutos automáticamente
def cargar_inteligencia():
    try:
        df = pd.read_csv(SHEET_URL)
        # Aseguramos que las columnas existan (deben coincidir con tus cabeceras en la Sheet)
        # Ordenamos para mostrar lo más reciente arriba
        return df.iloc[::-1] 
    except Exception as e:
        return pd.DataFrame()

# --- 5. INTERFAZ SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    tasa, variacion = calcular_variacion_real(alcance)
    st.metric(label="Tasa Oficial BCV", value=f"{tasa:.4f} Bs", delta=f"{variacion:+.2f}%")
    st.metric("Riesgo País (EMBI)", "18,450 bps", "-50 bps", delta_color="inverse")
    st.divider()
    st.write("📊 **Monitor de Energía**")
    st.caption("Cesta OPEP: $79.40 (+0.5%)")

# --- 6. CUERPO PRINCIPAL ---
st.title("🛡️ Public Go: Strategic Insight Dashboard")
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}**")

# Categorías que queremos mostrar
CATEGORIAS_FILTRO = ["GOBIERNO", "ENERGÍA", "ECONOMÍA", "RELACIONES"]

# Botón de actualización manual
if st.button("🔄 SINCRONIZAR INTELIGENCIA"):
    st.cache_data.clear()
    st.rerun()

df_intel = cargar_inteligencia()

if not df_intel.empty:
    # Mostramos los reportes procesados por Pabbly + Gemini
    for index, row in df_intel.iterrows():
        # Intentamos determinar la categoría por palabras clave si no la tienes en la Sheet
        # O simplemente mostramos el flujo de noticias analizadas
        st.markdown(f"<div class='cat-header'>ANÁLISIS ESTRATÉGICO</div>", unsafe_allow_html=True)
        
        col_n, col_d = st.columns([1.5, 2])
        
        with col_n:
            st.write("**📌 Fuente Original**")
            st.markdown(f"""
                <div class='news-item'>
                    <a href='{row['Link']}' target='_blank' class='news-link'>{row['Noticia']}</a>
                    <p style='font-size: 0.8rem; color: gray;'>Fecha: {row['Fecha']}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_d:
            st.write("**🧠 Inteligencia Public Go**")
            st.markdown(f"<div class='analysis-box'>{row['Analisis']}</div>", unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontraron datos en la base de datos. Asegúrate de que Pabbly haya procesado al menos una noticia y que el ID de la Google Sheet sea correcto.")

st.divider()
st.caption("Uso exclusivo Public Go Consultores. Sistema automatizado via Pabbly Connect.")
