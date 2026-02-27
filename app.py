import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# --- CONEXIÓN IA (Versión Pro Estable) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

model = conectar_ia()

st.set_page_config(page_title="Public Go Elite", layout="wide")

# --- ESTILOS (Tu diseño azul) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; }
    .news-item { border-bottom: 1px solid #f0f0f0; padding: 10px 0; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: bold; font-size: 1rem; }
    .risk-box { border-left: 8px solid #003b5c; background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE BÚSQUEDA (Reforzado) ---
def buscar_noticias(query, periodo):
    # Simplificamos la query para asegurar que traiga resultados
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:5]:
            results.append({"titulo": item.title.get_text().split(" - ")[0], "link": item.link.get_text()})
    except:
        pass
    return results

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro:", ["Hoy", "Semana", "Mes"])
    codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}
    st.divider()
    st.metric("Tasa BCV", "417.35 Bs", "+0.79%")

# --- CUERPO PRINCIPAL ---
st.title("🛡️ Strategic Insight Dashboard")

CATEGORIAS = {
    "🏛️ GOBIERNO & PODER": 'Venezuela (Delcy OR Fiscalía OR Diosdado OR Nombramiento OR renuncia OR Ministro)',
    "🛢️ ENERGÍA & LICENCIAS": 'Venezuela (Chevron OR Shell OR PDVSA OR Licencia)',
    "💰 ECONOMÍA & CONSUMO": 'Venezuela (BCV OR dólar OR inflación)'
}

if st.button("🚀 GENERAR REPORTE"):
    st.session_state['run'] = True

if st.session_state.get('run'):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_noticias(q, codigos[alcance])
        
        if noticias:
            col1, col2 = st.columns([1.5, 1.5])
            with col1:
                st.write("**📌 Noticias Detectadas**")
                titulares_texto = ""
                for n in noticias:
                    st.markdown(f"<div class='news-item'><a href='{n['link']}' target='_blank' class='news-link'>{n['titulo']}</a></div>", unsafe_allow_html=True)
                    titulares_texto += f"- {n['titulo']}\n"
            
            with col2:
                st.write("**🧠 Análisis de Riesgo**")
                # El análisis solo ocurre si presionas el botón de esa categoría
                if st.button(f"Analizar {
