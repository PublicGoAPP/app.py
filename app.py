import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import re

# --- CONFIGURACIÓN DE IA ULTRA-ROBUSTA ---
def conectar_con_mejor_modelo():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en Secrets.")
        return None
    
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    try:
        # Paso 1: Listar modelos para evitar el error 404 de "nombre no encontrado"
        modelos_validos = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos_validos.append(m.name)
        
        if not modelos_validos:
            return None
            
        # Prioridad: 1.5 Flash -> 1.5 Pro -> Pro -> El que sea
        prioridad = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        for p in prioridad:
            if p in modelos_validos:
                return genai.GenerativeModel(p)
        
        return genai.GenerativeModel(modelos_validos[0])
    except Exception as e:
        # Si falla el listado (por región), intentamos la ruta directa clásica
        return genai.GenerativeModel('gemini-pro')

model = conectar_con_mejor_modelo()

st.set_page_config(page_title="Public Go Elite", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .analysis-box { background-color: #f0f7f9; padding: 20px; border-left: 6px solid #003b5c; border-radius: 5px; margin-bottom: 20px; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 15px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
def generar_analisis_ia(cat, data, alcance):
    if not model: return "Error crítico: No se detectó motor de IA disponible."
    
    # Limpieza profunda de titulares para la IA
    titulares = " | ".join([n['titulo'].split(" - ")[0] for n in data])
    
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. Analiza estos eventos de {cat} en Venezuela (Periodo: {alcance}):
    {titulares}. 
    
    Tu informe para el 27 de febrero de 2026 debe incluir:
    1. DIAGNÓSTICO ESTRATÉGICO: ¿Qué cambió en la narrativa o el poder?
    2. ANÁLISIS CUANTITATIVO: Explica la relevancia de las cifras detectadas (si las hay).
    3. ACCIÓN RECOMENDADA: Una decisión para clientes corporativos.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ La IA está bloqueada. Detalle: {str(e)[:60]}"

def buscar_noticias_rss(query, periodo_cod):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo_cod}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:10]:
            results.append({
                "titulo": item.title.get_text(),
                "link": item.link.get_text(),
                "desc": item.description.get_text()
            })
    except: pass
    return results

def extraer_cifras_v5(texto):
    patrones = [r'\d+(?:\.\d+)?%', r'\$\s?\d+(?:\.\d+)?', r'Bs\s?\d+(?:\.\d+)?', r'\d+\s?liberados', r'\d+\s?mil\s?millones']
    encontrados = re.findall("|".join(patrones), texto, re.IGNORECASE)
    return list(set(encontrados))

# --- INTERFAZ ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("Tasa BCV", "417,35 Bs/$", "+0,8%")
    st.metric("PIB 2026", "10%", "Proyectado")

st.title("🛡️ Public Go: AI Intelligence Hub")
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR Larry Devoe OR Amnistia OR Saab)',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Repsol OR PDVSA OR gas)',
    "💰 ECONOMÍA": 'Venezuela (PIB OR BCV OR dolar OR inversion)',
    "🌎 RELACIONES": 'Venezuela (Trump OR socio OR amigo OR sanciones)'
}

codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if st.button("🚀 GENERAR INTELIGENCIA Y ANALÍTICA"):
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
                cifras = extraer_cifras_v5(texto_total)
                if cifras:
                    for c in cifras: st.success(c)
                else: st.caption("No se detectaron cifras nuevas.")

            for n in noticias:
                with st.expander(f"📌 {n['titulo'].split(' - ')[0]}"):
                    st.caption(f"[Fuente]({n['link']})")
        else:
            st.info("Sin actualizaciones para este eje.")
