import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go Elite v75", layout="wide")

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
    .report-card { background-color: #f8f9fa; padding: 25px; border-radius: 5px; border-top: 4px solid #003b5c; margin-bottom: 35px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .noticia-titulo { color: #003b5c; font-weight: bold; font-size: 1.2rem; line-height: 1.3; margin-bottom: 10px; }
    .analisis-box { background-color: #ffffff; padding: 15px; border-left: 4px solid #003b5c; border-radius: 4px; font-size: 0.95rem; color: #333; line-height: 1.6; margin-bottom: 15px; }
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
        df.columns = df.columns.str.strip() 
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

# Mapeo oficial de colores
color_map = {
    "PETRÓLEO": "#E67E22", "ECONOMÍA": "#27AE60", 
    "POLÍTICA": "#2980B9", "RELACIONES INTERNACIONALES": "#C0392B",
    "GENERAL": "#7F8C8D"
}

if not df_intel.empty:
    for _, row in df_intel.iterrows():
        # --- LÓGICA DE LIMPIEZA DE CATEGORÍA ---
        raw_cat = str(row.get('Categoría', 'GENERAL')).upper()
        
        if "PETRÓLEO" in raw_cat or "PETROLEO" in raw_cat:
            clean_cat, bg_color = "PETRÓLEO", color_map["PETRÓLEO"]
        elif "ECONOMÍA" in raw_cat or "ECONOMIA" in raw_cat:
            clean_cat, bg_color = "ECONOMÍA", color_map["ECONOMÍA"]
        elif "POLÍTICA" in raw_cat or "POLITICA" in raw_cat:
            clean_cat, bg_color = "POLÍTICA", color_map["POLÍTICA"]
        elif "RELACIONES" in raw_cat:
            clean_cat, bg_color = "RELACIONES INTERNACIONALES", color_map["RELACIONES INTERNACIONALES"]
        else:
            clean_cat, bg_color = "GENERAL", color_map["GENERAL"]

        # --- PROCESAMIENTO ESTRUCTURADO DEL ANÁLISIS ---
        # Limpieza inicial de etiquetas de control
        texto_full = str(row["Analisis"]).replace("SEPARADOR", "").split("CATEGORIA:")[0].strip()
        
        # Segmentación: Buscamos la palabra "RECOMENDACIÓN" o el uso de negritas finales
        if "RECOMENDACIÓN" in texto_full.upper():
            partes = texto_full.upper().split("RECOMENDACIÓN", 1)
            cuerpo = texto_full[:len(partes[0])].strip()
            # Quitamos los dos puntos si existen al inicio de la recomendación
            rec_texto = texto_full[len(partes[0])+14:].strip().lstrip(":") 
        else:
            # Si no hay palabra clave, intentamos separar por el último bloque en negrita
            partes = texto_full.split("**")
            if len(partes) > 1:
                cuerpo = partes[0].strip()
                rec_texto = partes[-1].strip()
            else:
                cuerpo = texto_full
                rec_texto = ""

        with st.container():
            st.markdown(f'<div class="report-card">', unsafe_allow_html=True)
            col_info, col_anid = st.columns([1, 2])
            
            with col_info:
                st.markdown(f'<span class="cat-tag" style="background-color: {bg_color}; color: white;">{clean_cat}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="noticia-titulo">{row["Noticia"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<a href="{row["Link"]}" target="_blank" class="fuente-link">🔗 Leer fuente original</a>', unsafe_allow_html=True)
                st.caption(f"📅 Corte Informativo")

            with col_anid:
                st.markdown("##### 🧠 Perspectiva Estratégica")
                st.markdown(f'<div class="analisis-box">{cuerpo}</div>', unsafe_allow_html=True)
                
                if rec_texto:
                    st.info(f"**💡 RECOMENDACIÓN EJECUTIVA:** \n{rec_texto}")
            
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Sincronizando con la central de inteligencia...")

st.divider()
st.caption("Uso exclusivo Public Go Consultores.")
