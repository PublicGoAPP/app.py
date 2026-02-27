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
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px; }
    .analysis-box { background-color: #f0f7f9; padding: 20px; border-left: 6px solid #003b5c; margin-bottom: 15px; border-radius: 5px; line-height: 1.6; }
    .metric-card { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE ANÁLISIS ---
def extraer_cifras(texto):
    # Patrones mejorados para detectar economía venezolana 2026
    patrones = [
        r'\d+(?:\.\d+)?%',            # Porcentajes
        r'\$\s?\d+(?:\.\d+)?',        # Dólares
        r'Bs\s?\d+(?:\.\d+)?',        # Bolívares
        r'\d+\s?liberados',           # Casos Amnistía
        r'PIB del\s?\d+%',            # Crecimiento
        r'\d+\s?mil\s?millones'       # Montos grandes
    ]
    encontrados = []
    for p in patrones:
        encontrados.extend(re.findall(p, texto, re.IGNORECASE))
    return list(set(encontrados))

def generar_analisis_ia(cat, data, alcance):
    # Limpiamos los titulares de ruidos (nombres de diarios, guiones, etc)
    titulares = " | ".join([n['titulo'].split(" - ")[0] for n in data])
    
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. Tu cliente es una multinacional en Venezuela.
    Analiza estos eventos de {cat} del periodo {alcance} de febrero 2026:
    {titulares}. 

    Realiza un análisis profesional INTEGRADO (Cualitativo y Cuantitativo):
    1. LECTURA ESTRATÉGICA: Sintetiza los hechos. ¿Es una señal de apertura, riesgo o estabilidad?
    2. IMPACTO EN CIFRAS: Si hay números, explícalos. Si no los hay en el texto, proyecta el impacto económico basado en que el PIB 2026 crece al 10%.
    3. ACCIÓN RECOMENDADA: Una decisión concreta para la gerencia hoy 27 de febrero.
    
    Sé directa, usa tono de consultoría de élite.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ El motor de IA está saturado. Intente de nuevo en 10 segundos. (Detalle: {str(e)[:50]})"

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
    alcance = st.radio("Alcance:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("PIB Proyectado 2026", "10%", "+2.5%")
    st.metric("Riesgo País", "Moderado", "Tendencia Estable")

st.title("🛡️ Public Go: AI Intelligence Hub")
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}** | Consultoría de Entorno")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR "Larry Devoe" OR "Amnistia" OR "Saab")',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR "PDVSA" OR "gas" OR "crudo")',
    "💰 ECONOMÍA": 'Venezuela (PIB OR "BCV" OR "dolar" OR "inversion")',
    "🇺🇸 RELACIONES": 'Venezuela (Trump OR "Washington" OR "Sanciones" OR "socio")'
}

codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if st.button("🚀 GENERAR INTELIGENCIA Y ANALÍTICA"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_noticias_rss(q, codigos[alcance])
        
        if noticias:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # El "corazón" de la IA
                analisis = generar_analisis_ia(cat, noticias, alcance)
                st.markdown(f"<div class='analysis-box'>{analisis}</div>", unsafe_allow_html=True)
            
            with col2:
                st.write("**📊 Datos Extraídos:**")
                # Unimos títulos y descripciones para que no se escape ningún número
                texto_total = " ".join([n['titulo'] + " " + n['desc'] for n in noticias])
                cifras = extraer_cifras(texto_total)
                if cifras:
                    for cifra in cifras:
                        st.markdown(f"✅ **{cifra}**")
                else:
                    st.caption("No se detectaron cifras específicas en los titulares. La IA generará proyecciones en el bloque de la izquierda.")

            # Desplegable de noticias para referencia rápida
            for n in noticias:
                with st.expander(f"📌 {n['titulo'].split(' - ')[0]}"):
                    st.write(n['desc'])
                    st.caption(f"[Fuente Oficial]({n['link']})")
        else:
            st.info(f"No se detectaron movimientos críticos en el eje de {cat} para este periodo.")

st.divider()
st.caption("Documento generado para uso estratégico de Public Go Consultores.")
