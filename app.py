import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import re

# --- SEGURIDAD: CONFIGURACIÓN ROBUSTA ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Cambiamos a 'gemini-pro' que es la ruta más estable para evitar el error 404
        model = genai.GenerativeModel('gemini-pro')
    else:
        st.error("⚠️ Configura la 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
except Exception as e:
    st.error(f"⚠️ Error de inicio: {e}")

st.set_page_config(page_title="Public Go Elite Analytics", layout="wide")

# --- ESTILOS PUBLIC GO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; }
    .analysis-box { background-color: #f0f7f9; padding: 20px; border-left: 6px solid #003b5c; margin-bottom: 15px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE INTELIGENCIA ---
def extraer_cifras_v2(texto):
    # Captura montos, porcentajes y cifras de impacto
    patrones = [
        r'\d+(?:\.\d+)?%',                    # Porcentajes
        r'\$\s?\d+(?:\.\d+)?(?:\s?millones)?', # Montos en $
        r'Bs\s?\d+(?:\.\d+)?',                # Bolívares
        r'\d+\s?liberados'                    # Datos de Amnistía
    ]
    encontrados = []
    for p in patrones:
        encontrados.extend(re.findall(p, texto, re.IGNORECASE))
    return list(set(encontrados))

def generar_analisis_ia(cat, data, alcance):
    titulares = " | ".join([n['titulo'].split(" - ")[0] for n in data])
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. 
    Analiza con rigor cualitativo y cuantitativo estos titulares de {cat} en Venezuela ({alcance} de febrero 2026):
    {titulares}. 

    Genera:
    1. DIAGNÓSTICO: ¿Qué está cambiando realmente hoy 27 de febrero?
    2. CIFRA DE IMPACTO: Explica la relevancia de los montos o datos detectados.
    3. RECOMENDACIÓN EJECUTIVA: Acción inmediata para Empire Keeway o similares.
    """
    try:
        # Forzamos la generación con el modelo configurado
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error de conexión con la IA: {str(e)[:50]}. Verifique que su API Key tenga acceso a Gemini Pro."

def buscar_noticias_rss(query, periodo_cod):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo_cod}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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

# --- INTERFAZ ---
with st.sidebar:
    st.markdown("### 🛡️ Dashboard Public Go")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana"])
    st.divider()
    st.metric("PIB 2026", "10%", "Proyección")
    st.metric("Tasa BCV", "417,35 Bs/$", "+0,8%")

st.title("🛡️ Public Go: AI Intelligence Hub")
st.write(f"Inteligencia generada el: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR "Larry Devoe" OR "Amnistia" OR "Saab")',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR "PDVSA" OR gas OR crudo)',
    "💰 ECONOMÍA": 'Venezuela (PIB OR BCV OR dolar OR inversion)',
    "🇺🇸 RELACIONES": 'Venezuela (Trump OR "Washington" OR "socio" OR "amigo")'
}

codigos = {"Hoy": "1d", "Semana": "7d"}

if st.button("🚀 ACTUALIZAR INTELIGENCIA"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_noticias_rss(q, codigos[alcance])
        
        if noticias:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"<div class='analysis-box'>{generar_analisis_ia(cat, noticias, alcance)}</div>", unsafe_allow_html=True)
            with col2:
                st.write("**📊 Datos Extraídos:**")
                texto_total = " ".join([n['titulo'] + " " + n['desc'] for n in noticias])
                cifras = extraer_cifras_v2(texto_total)
                if cifras:
                    for cifra in cifras:
                        st.markdown(f"✅ **{cifra}**")
                else: st.caption("No se detectaron cifras nuevas.")

            for n in noticias:
                with st.expander(f"📌 {n['titulo'].split(' - ')[0]}"):
                    st.caption(f"[Fuente Oficial]({n['link']})")
        else: st.info("Sin actualizaciones críticas.")

st.divider()
st.caption("Uso exclusivo de Public Go Consultores.")
