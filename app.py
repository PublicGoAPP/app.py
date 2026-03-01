import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go Elite v72", layout="wide")

# --- 1. CONFIGURACIÓN DE LA FUENTE (GOOGLE SHEETS) ---
SHEET_ID = "1147SVSNiHRlM74tVcn36T2PzMqTPOGulHcEt8AMKUMc" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- 2. ESTILOS VISUALES CORPORATIVOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-tag { padding: 4px 12px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: inline-block; }
    .report-card { background-color: #f8f9fa; padding: 20px; border-radius: 5px; border-top: 4px solid #003b5c; margin-bottom: 30px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .noticia-titulo { color: #003b5c; font-weight: bold; font-size: 1.15rem; line-height: 1.3; margin-bottom: 10px; }
    .analisis-box { background-color: #ffffff; padding: 15px; border-left: 4px solid #003b5c; border-radius: 4px; font-size: 0.95rem; color: #333; line-height: 1.5; }
    .fuente-link { color: #003b5c; text-decoration: none; font-weight: 600; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE INDICADORES (SIDEBAR) ---
def obtener_indicadores(alcance):
    tasa_actual = 417.3579
    variaciones = {"Hoy": +0.85, "Semana": +1.20, "Mes": +3.45}
    return tasa_actual, variaciones.get(alcance, 0)

# --- 4. MOTOR DE CARGA ---
@st.cache_data(ttl=300)
def cargar_datos_estrategicos():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip() # Limpia espacios en nombres de columnas
        return df.iloc[::-1]
    except Exception as e:
        return pd.DataFrame()

# --- 5. INTERFAZ SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Public Go")
    st.divider()
    alcance = st.radio("Filtro de Entorno:", ["Hoy", "Semana", "Mes"])
    tasa, delta = obtener_indicadores(alcance)
    st.metric(label="Tasa Oficial BCV", value=f"{tasa:.4f} Bs", delta=f"{delta}%")
    st.metric("Riesgo País (EMBI)", "18,450 bps", "-50 bps", delta_color="inverse")
    st.divider()
    st.caption("Cesta OPEP: $79.40 (+0.5%)")
    st.caption("Producción PDVSA: 870k bpd")

# --- 6. CUERPO PRINCIPAL ---
st.title("🛡️ Public Go: Strategic Insight Dashboard")
st.write(f"Corte de Inteligencia: **{datetime.now().strftime('%d/%m/%Y')}**")

if st.button("🔄 ACTUALIZAR REPORTES"):
    st.cache_data.clear()
    st.rerun()

df_intel = cargar_datos_estrategicos()

# Mapeo de colores para categorías
color_map = {
    "PETRÓLEO": "#E67E22", "ECONOMÍA": "#27AE60", 
    "POLÍTICA": "#2980B9", "RELACIONES INTERNACIONALES": "#C0392B"
}

if not df_intel.empty:
    for _, row in df_intel.iterrows():
        # Buscamos la columna de categoría (manejando posibles tildes o variaciones)
        cat_val = row.get('Categoría', row.get('Categoria', 'GENERAL'))
        categoria_label = str(cat_val).upper().strip()
        bg_color = color_map.get(categoria_label, "#7F8C8D")
        
        # Diseño de dos columnas: Noticia (izq) | Análisis (der)
        with st.container():
            st.markdown(f'<div class="report-card">', unsafe_allow_html=True)
            col_info, col_anid = st.columns([1.2, 2])
            
            with col_info:
                st.markdown(f'<span class="cat-tag" style="background-color: {bg_color}; color: white;">{categoria_label}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="noticia-titulo">{row["Noticia"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<a href="{row["Link"]}" target="_blank" class="fuente-link">🔗 Leer fuente</a>', unsafe_allow_html=True)
                st.caption(f"Fecha: {row.get('Fecha', 'Reciente')}")

            with col_anid:
                st.markdown("**🧠 ANÁLISIS ESTRATÉGICO**")
                st.markdown(f'<div class="analisis-box">{row["Analisis"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No hay datos nuevos. Verifica que Pabbly esté enviando la información a la Google Sheet.")

st.divider()
st.caption("Uso exclusivo Public Go Consultores.")
