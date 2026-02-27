import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error: Configure su API Key en los Secrets de Streamlit.")

st.set_page_config(page_title="Public Go Elite", layout="wide")

# --- DISEÑO CORPORATIVO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 20px; }
    .analysis-box { background-color: #f0f7f9; padding: 15px; border-left: 6px solid #003b5c; margin-bottom: 20px; border-radius: 0 0 8px 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE BÚSQUEDA RSS (MÁS ESTABLE) ---
def buscar_noticias_rss(query, periodo_cod):
    # periodo_cod puede ser 'd' (día), 'w' (semana), 'm' (mes)
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
                "fecha": item.pubDate.get_text()
            })
    except: pass
    return results

# --- INTERFAZ ---
with st.sidebar:
    st.markdown("### 🛡️ Radar Public Go")
    alcance = st.radio("Alcance Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("PIB 2026 (Est.)", "10%", "+2.5%")
    st.metric("Riesgo País", "Moderado", "Estable")

st.markdown("<h1 style='color: #003b5c;'>Public Go: Intelligence Insight Hub</h1>", unsafe_allow_html=True)
st.write(f"Análisis generado el: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR "Larry Devoe" OR "Amnistia" OR "Saab")',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR "PDVSA" OR "gas" OR "crudo")',
    "💰 ECONOMÍA": 'Venezuela (PIB OR "BCV" OR "dolar" OR "inversion")',
    "🇺🇸 RELACIONES": 'Venezuela (Trump OR "Washington" OR "Sanciones")'
}

codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if st.button("🚀 ACTUALIZAR INTELIGENCIA"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_noticias_rss(q, codigos[alcance])
        
        if noticias:
            titulares = " | ".join([n['titulo'] for n in noticias])
            prompt = f"Eres consultora de Public Go. Analiza estos hechos de {cat} en Venezuela para el periodo {alcance}: {titulares}. Da 3 conclusiones estratégicas para el 27 de febrero de 2026."
            
            try:
                analisis = model.generate_content(prompt).text
                st.markdown(f"<div class='analysis-box'>{analisis}</div>", unsafe_allow_html=True)
            except: 
                st.info("Analizando tendencias del sector...")

            for n in noticias:
                st.markdown(f"📌 **{n['titulo']}** ([Fuente]({n['link']}))")
        else:
            st.markdown("<div class='analysis-box'>No se detectaron hitos críticos en este eje.</div>", unsafe_allow_html=True)
