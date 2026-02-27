import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import re

# --- CONFIGURACIÓN DE IA (CONEXIÓN 2026) ---
def conectar_cerebro():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en Secrets.")
        return None
    
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos la ruta completa del modelo para evitar el error 404
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

model = conectar_cerebro()

st.set_page_config(page_title="Public Go Elite", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .analysis-box { background-color: #f0f7f9; padding: 20px; border-left: 6px solid #003b5c; border-radius: 5px; margin-bottom: 20px; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INTELIGENCIA ---
def generar_analisis(cat, noticias):
    if not model: return "Cerebro desconectado."
    titulares = " | ".join([n['titulo'] for n in noticias])
    prompt = f"Como Directora de Public Go, analiza estos hechos de {cat} en Venezuela hoy 27 de febrero 2026: {titulares}. Da un diagnóstico cualitativo y cuantitativo breve."
    try:
        return model.generate_content(prompt).text
    except:
        return "Analizando entorno estratégico..."

def buscar_rss(query, periodo):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo}&hl=es-419&gl=VE&ceid=VE:es-419"
    res = []
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:8]:
            res.append({"titulo": item.title.get_text(), "link": item.link.get_text(), "desc": item.description.get_text()})
    except: pass
    return res

# --- INTERFAZ ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro:", ["1d", "7d"])
    st.divider()
    st.metric("Tasa BCV", "417,35 Bs/$", "+0,8%")

st.title("🛡️ Intelligence Insight Hub")
st.write(f"Corte: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR "Larry Devoe" OR "Saab" OR "Amnistia")',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR "PDVSA" OR gas)',
    "💰 ECONOMÍA": 'Venezuela (PIB OR BCV OR dolar OR inversion)',
    "🇺🇸 RELACIONES": 'Venezuela (Trump OR socio OR amigo OR sanciones)'
}

if st.button("🚀 ACTUALIZAR INTELIGENCIA"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        data = buscar_rss(q, alcance)
        if data:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"<div class='analysis-box'>{generar_analisis(cat, data)}</div>", unsafe_allow_html=True)
            with col2:
                st.write("**📊 Cifras detectadas:**")
                texto = " ".join([n['titulo'] + n['desc'] for n in data])
                cifras = list(set(re.findall(r'\d+(?:\.\d+)?%|\$\s?\d+|Bs\s?\d+', texto)))
                for c in cifras: st.success(c)
            for n in data:
                with st.expander(f"📌 {n['titulo'].split(' - ')[0]}"):
                    st.caption(f"[Fuente Oficial]({n['link']})")
