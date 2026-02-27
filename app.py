import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import re

# --- CONFIGURACIÓN DE IA (OMNI-CONEXIÓN v53 BASE) ---
def conectar_ia_robusta():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en los Secrets de Streamlit.")
        return None
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    try:
        modelos_validos = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos_validos.append(m.name)
        prioridad = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        for p in prioridad:
            if p in modelos_validos:
                return genai.GenerativeModel(p)
        return genai.GenerativeModel(modelos_validos[0]) if modelos_validos else None
    except:
        return genai.GenerativeModel('gemini-pro')

model = conectar_ia_robusta()

st.set_page_config(page_title="Public Go Elite v55", layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .analysis-box { background-color: #f0f7f9; padding: 15px; border-left: 5px solid #003b5c; border-radius: 5px; font-size: 0.95rem; line-height: 1.5; }
    .news-item { border-bottom: 1px solid #eee; padding: 10px 0; }
    .metric-badge { background-color: #e8f5e9; color: #2e7d32; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.85rem; margin-bottom: 5px; display: block; width: fit-content; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
def generar_analisis_estratégico(cat, data, alcance):
    if not model: return "Error de conexión con el motor de IA."
    titulares = " | ".join([n['titulo'].split(" - ")[0] for n in data])
    prompt = f"Eres Directora Estratégica de Public Go. Analiza estos hechos de {cat} en Venezuela ({alcance}) para hoy 27 de febrero 2026: {titulares}. Da un diagnóstico cualitativo y cuantitativo conciso."
    try:
        return model.generate_content(prompt).text
    except:
        return "El análisis cualitativo está siendo procesado..."

def buscar_rss_profundo(query, periodo_cod):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo_cod}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:7]:
            results.append({"titulo": item.title.get_text(), "link": item.link.get_text(), "desc": item.description.get_text()})
    except: pass
    return results

def detectar_cifras(texto):
    patrones = [r'\d+(?:\.\d+)?%', r'\$\s?\d+(?:\.\d+)?', r'Bs\s?\d+(?:\.\d+)?', r'\d+\s?liberados']
    hallados = re.findall("|".join(patrones), texto, re.IGNORECASE)
    return list(set(hallados))

# --- INTERFAZ ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Alcance Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("Tasa BCV", "417,35 Bs/$", "+0,8%")
    st.metric("PIB 2026", "10%", "Proyectado")

st.title("🛡️ Public Go: AI Strategic Hub")
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR Larry Devoe OR Amnistia OR Saab)',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Repsol OR PDVSA OR gas)',
    "💰 ECONOMÍA": 'Venezuela (PIB OR BCV OR dolar OR inversion)',
    "🌎 RELACIONES": 'Venezuela (Trump OR socio OR amigo OR sanciones)'
}

codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if st.button("🚀 ACTUALIZAR REPORTE"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss_profundo(q, codigos[alcance])
        
        if noticias:
            # Determinamos si hay cifras para ajustar el diseño de columnas
            texto_total = " ".join([n['titulo'] + " " + n['desc'] for n in noticias])
            cifras_encontradas = detectar_cifras(texto_total)
            
            # Si hay cifras usamos 3 columnas, si no, usamos 2 para dar más espacio a las noticias
            if cifras_encontradas:
                col_diag, col_news, col_cifras = st.columns([1.2, 1.8, 0.6])
            else:
                col_diag, col_news = st.columns([1.2, 2.4])
            
            with col_diag:
                st.write("**🧠 Diagnóstico**")
                st.markdown(f"<div class='analysis-box'>{generar_analisis_estratégico(cat, noticias, alcance)}</div>", unsafe_allow_html=True)
            
            with col_news:
                st.write("**📌 Noticias**")
                for n in noticias:
                    st.markdown(f"""<div class='news-item'><a href='{n['link']}' target='_blank' style='color:#003b5c; text-decoration:none; font-weight:500;'>{n['titulo'].split(' - ')[0]}</a></div>""", unsafe_allow_html=True)
            
            if cifras_encontradas:
                with col_cifras:
                    st.write("**📊 Cifras**")
                    for c in cifras_encontradas:
                        st.markdown(f"<span class='metric-badge'>✅ {c}</span>", unsafe_allow_html=True)
        else:
            st.info(f"Sin novedades significativas en el eje de {cat}.")

st.divider()
st.caption("Uso exclusivo Public Go Consultores. Reporte basado en IA y datos OSINT.")
