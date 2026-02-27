import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import re

# --- SEGURIDAD: CONFIGURACIÓN MULTI-MODELO ---
def configurar_ia():
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            # Intentamos con la versión más reciente, si falla, el sistema avisará
            return genai.GenerativeModel('gemini-1.5-flash')
        else:
            st.error("⚠️ Configura la 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
            return None
    except:
        # Intento de respaldo con modelo Pro si el Flash falla por versión
        return genai.GenerativeModel('gemini-pro')

model = configurar_ia()

st.set_page_config(page_title="Public Go Elite Analytics", layout="wide")

# --- ESTILOS PUBLIC GO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; }
    .analysis-box { background-color: #f0f7f9; padding: 20px; border-left: 6px solid #003b5c; margin-bottom: 15px; border-radius: 5px; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE INTELIGENCIA ---
def generar_analisis_ia(cat, data, alcance):
    titulares = " | ".join([n['titulo'].split(" - ")[0] for n in data])
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. 
    Analiza con rigor cualitativo y cuantitativo estos titulares de {cat} en Venezuela ({alcance} de febrero 2026):
    {titulares}. 

    Genera:
    1. DIAGNÓSTICO: ¿Qué está cambiando realmente hoy 27 de febrero?
    2. CIFRA DE IMPACTO: Explica la relevancia de los montos o datos detectados.
    3. RECOMENDACIÓN EJECUTIVA: Acción inmediata para la gerencia.
    """
    try:
        # Sistema de reintento interno
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Nota: El motor de IA está en mantenimiento o la clave es inválida. Detalle: {str(e)[:40]}"

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

def extraer_cifras_v3(texto):
    patrones = [r'\d+(?:\.\d+)?%', r'\$\s?\d+(?:\.\d+)?', r'Bs\s?\d+(?:\.\d+)?', r'\d+\s?liberados']
    encontrados = []
    for p in patrones:
        encontrados.extend(re.findall(p, texto, re.IGNORECASE))
    return list(set(encontrados))

# --- INTERFAZ ---
with st.sidebar:
    st.markdown("### 🛡️ Dashboard Public Go")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana"])
    st.divider()
    st.metric("Tasa BCV", "417,35 Bs/$", "+0,8% [27-Feb]")
    st.metric("PIB 2026", "10%", "Proyectado")

st.title("🛡️ Public Go: Strategic Insight Hub")
st.write(f"Corte de Inteligencia: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR Larry Devoe OR Amnistia OR Saab)',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Repsol OR PDVSA OR gas OR crudo)',
    "💰 ECONOMÍA": 'Venezuela (PIB OR BCV OR dolar OR inversion)',
    "🌎 RELACIONES": 'Venezuela (Trump OR Washington OR socio OR amigo)'
}

periodos = {"Hoy": "1d", "Semana": "7d"}

if st.button("🚀 ACTUALIZAR REPORTE"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_noticias_rss(q, periodos[alcance])
        
        if noticias:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"<div class='analysis-box'>{generar_analisis_ia(cat, noticias, alcance)}</div>", unsafe_allow_html=True)
            with col2:
                st.write("**📊 Datos Detectados:**")
                texto_total = " ".join([n['titulo'] + " " + n['desc'] for n in noticias])
                cifras = extraer_cifras_v3(texto_total)
                if cifras:
                    for c in cifras: st.markdown(f"✅ **{c}**")
                else: st.caption("No se hallaron cifras.")

            for n in noticias:
                with st.expander(f"📌 {n['titulo'].split(' - ')[0]}"):
                    st.caption(f"[Fuente]({n['link']})")
        else: st.info("Sin actualizaciones.")
