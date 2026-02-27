import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import re

# --- SEGURIDAD Y CONFIGURACIÓN ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error: Configure su API Key en los Secrets de Streamlit.")

st.set_page_config(page_title="Public Go Elite Analytics", layout="wide")

# --- ESTILOS PUBLIC GO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; }
    .analysis-box { background-color: #f0f7f9; padding: 15px; border-left: 5px solid #003b5c; margin-bottom: 15px; border-radius: 5px; }
    .metric-card { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE ANÁLISIS ---
def extraer_cifras(texto):
    # Extrae porcentajes, montos en $ o números de personas (ej. liberados)
    patrones = [r'\d+%', r'\$\d+', r'\d+\s liberados', r'PIB del \d+']
    encontrados = []
    for p in patrones:
        encontrados.extend(re.findall(p, texto))
    return list(set(encontrados))

def generar_analisis_ia(cat, data, alcance):
    titulares = " | ".join([n['titulo'] for n in data])
    prompt = f"""
    Eres consultora senior de Public Go. Analiza estos eventos de {cat} en Venezuela para el periodo {alcance}:
    {titulares}. 
    
    Proporciona:
    1. TENDENCIA: ¿Hacia dónde se mueve el sector?
    2. INDICADOR CRÍTICO: Una cifra o hecho clave mencionado.
    3. RECOMENDACIÓN: Qué debe hacer una empresa transnacional hoy 27 de febrero de 2026.
    """
    try:
        return model.generate_content(prompt).text
    except:
        return "Análisis en procesamiento estratégico..."

def buscar_noticias_rss(query, periodo_cod):
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
    st.markdown("### 🛡️ Dashboard Public Go")
    alcance = st.radio("Alcance:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("PIB Proyectado", "10%", "+2.5%")
    st.metric("Riesgo País", "Moderado", "Estable")

st.title("🛡️ Public Go: AI Intelligence Hub")
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR "Larry Devoe" OR "Amnistia" OR "Saab")',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR "PDVSA" OR "gas" OR "crudo")',
    "💰 ECONOMÍA": 'Venezuela (PIB OR "BCV" OR "dolar" OR "inversion")',
    "🇺🇸 RELACIONES": 'Venezuela (Trump OR "Washington" OR "Sanciones")'
}

codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if st.button("🚀 GENERAR INTELIGENCIA Y ANALÍTICA"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_noticias_rss(q, codigos[alcance])
        
        if noticias:
            # IA y Análisis
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"<div class='analysis-box'>{generar_analisis_ia(cat, noticias, alcance)}</div>", unsafe_allow_html=True)
            
            with col2:
                st.write("**📊 Datos Extraídos:**")
                cifras = extraer_cifras(" ".join([n['titulo'] + n['desc'] for n in noticias]))
                if cifras:
                    for cifra in cifras:
                        st.markdown(f"✅ {cifra}")
                else:
                    st.caption("No se detectaron cifras específicas.")

            # Noticias
            for n in noticias:
                with st.expander(f"📌 {n['titulo']}"):
                    st.caption(f"[Fuente Oficial]({n['link']})")
        else:
            st.info("Sin hitos nuevos en este eje.")
