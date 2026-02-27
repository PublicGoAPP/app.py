import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import re

# --- CONFIGURACIÓN ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error: Configure su API Key en los Secrets de Streamlit.")

st.set_page_config(page_title="Public Go Intelligence Hub", layout="wide")

# --- ESTILOS CORPORATIVOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .analysis-card { background-color: #f0f7f9; padding: 20px; border-left: 6px solid #003b5c; border-radius: 5px; margin-bottom: 20px; }
    .metric-box { text-align: center; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR ANALÍTICO ---
def analizar_inteligencia_hibrida(cat, noticias, alcance):
    """
    Realiza análisis cuantitativo (cifras) y cualitativo (narrativa).
    """
    texto_noticias = " | ".join([f"{n['titulo']}: {n['desc']}" for n in noticias])
    
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. Realiza un análisis de INTELIGENCIA sobre {cat} en Venezuela para el {alcance} de febrero 2026.
    DATOS: {texto_noticias}
    
    ESTRUCTURA TU RESPUESTA:
    1. ANÁLISIS CUALITATIVO: Identifica el cambio de tono, actores clave y clima político/social.
    2. ANÁLISIS CUANTITATIVO: Extrae y analiza CUALQUIER cifra mencionada (tasas, porcentajes, montos, cantidades). Si no hay cifras en el texto, estima el impacto económico basado en tu conocimiento de 2026.
    3. IMPLICACIÓN ESTRATÉGICA: ¿Qué significa esto para el flujo de caja o la seguridad jurídica de una multinacional?
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Análisis técnico momentáneamente no disponible."

def buscar_noticias_estables(query, periodo_cod):
    # El motor que ya sabemos que no se bloquea
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo_cod}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:10]:
            results.append({
                "titulo": item.title.get_text(),
                "link": item.link.get_text(),
                "desc": item.description.get_text()
            })
    except: pass
    return results

# --- INTERFAZ ---
with st.sidebar:
    st.markdown("### 🛡️ Centro de Mando")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana"])
    st.divider()
    st.metric("Tasa BCV (27-F)", "417,35 Bs/$", "+0,8%")
    st.metric("Crecimiento Est.", "10% PIB", "Proyección 2026")

st.title("🛡️ Public Go: Strategic Insight Dashboard")
st.write(f"Corte de Inteligencia: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO Y TRANSICIÓN": 'Venezuela (Fiscal OR "Larry Devoe" OR "Amnistia" OR "Saab")',
    "🛢️ ENERGÍA Y PETRÓLEO": 'Venezuela (Shell OR Repsol OR "PDVSA" OR gas OR crudo)',
    "💰 ECONOMÍA Y NEGOCIOS": 'Venezuela (PIB OR BCV OR dolar OR inversion)',
    "🇺🇸 RELACIONES EXTERIORES": 'Venezuela (Trump OR diplomacia OR sanciones)'
}

periodos = {"Hoy": "1d", "Semana": "7d"}

if st.button("🚀 GENERAR REPORTE DE INTELIGENCIA"):
    for cat, q in CATEGORIAS.items():
        noticias = buscar_noticias_estables(q, periodos[alcance])
        
        st.markdown(f"### {cat}")
        if noticias:
            # Bloque de Análisis IA (Cualitativo + Cuantitativo)
            st.markdown(f"<div class='analysis-card'>{analizar_inteligencia_hibrida(cat, noticias, alcance)}</div>", unsafe_allow_html=True)
            
            # Acordeón de Fuentes
            with st.expander("Detalle de fuentes detectadas"):
                for n in noticias:
                    st.markdown(f"📌 **{n['titulo']}** \n [Ir a la fuente]({n['link']})")
        else:
            st.info("Sin actualizaciones críticas en este eje.")
