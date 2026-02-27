import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import re

# --- CONFIGURACIÓN DE IA (RUTA DE MODELO CORREGIDA) ---
def inicializar_cerebro():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Configura la 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
        return None
    
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # IMPORTANTE: Usamos la ruta completa 'models/...' para evitar el error 404
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"❌ Error al conectar con Google: {e}")
        return None

model = inicializar_cerebro()

st.set_page_config(page_title="Public Go Elite", layout="wide")

# --- ESTILOS PUBLIC GO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .analysis-box { background-color: #f0f7f9; padding: 20px; border-left: 6px solid #003b5c; border-radius: 5px; margin-bottom: 20px; font-size: 1.05rem; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE ANÁLISIS ---
def generar_analisis_ia(cat, data, alcance):
    if not model: return "IA no configurada correctamente."
    titulares = " | ".join([n['titulo'].split(" - ")[0] for n in data])
    prompt = f"""
    Como Directora de Estrategia de Public Go, analiza estos eventos de {cat} en Venezuela (Periodo: {alcance}):
    {titulares}. 
    
    Proporciona un análisis cualitativo y cuantitativo para el 27 de febrero de 2026.
    1. DIAGNÓSTICO: ¿Qué cambió hoy?
    2. CIFRA CLAVE: Análisis del dato más relevante.
    3. ACCIÓN: Recomendación para clientes.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ La IA aún no responde. Detalle: {str(e)[:50]}"

def buscar_noticias_rss(query, periodo_cod):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo_cod}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:10]:
            results.append({
                "titulo": item.title.get_text(),
                "link": item.link.get_text(),
                "desc": item.description.get_text()
            })
    except: pass
    return results

def extraer_cifras(texto):
    patrones = [r'\d+(?:\.\d+)?%', r'\$\s?\d+(?:\.\d+)?', r'Bs\s?\d+(?:\.\d+)?', r'\d+\s?liberados']
    encontrados = re.findall("|".join(patrones), texto, re.IGNORECASE)
    return list(set(encontrados))

# --- INTERFAZ ---
with st.sidebar:
    st.title("🛡️ Public Go")
    # RECUPERADA LA OPCIÓN DE MES
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("Tasa BCV", "417,35 Bs/$", "+0,8%")
    st.metric("PIB 2026", "10%", "Estable")

st.title("🛡️ Public Go: Strategic Insight Dashboard")
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
        noticias = buscar_noticias_rss(q, codigos[alcance])
        
        if noticias:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"<div class='analysis-box'>{generar_analisis_ia(cat, noticias, alcance)}</div>", unsafe_allow_html=True)
            with col2:
                st.write("**📊 Cifras Detectadas:**")
                texto_total = " ".join([n['titulo'] + " " + n['desc'] for n in noticias])
                cifras = extraer_cifras(texto_total)
                if cifras:
                    for c in cifras: st.success(c)
                else: st.caption("No se hallaron cifras en los titulares.")

            for n in noticias:
                with st.expander(f"📌 {n['titulo'].split(' - ')[0]}"):
                    st.caption(f"[Fuente]({n['link']})")
        else:
            st.info("Sin actualizaciones para este periodo.")
