import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import re

# --- CONFIGURACIÓN DE IA (OMNI-CONEXIÓN v53 BASE) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en Secrets.")
        return None
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    try:
        # Probamos modelos por orden de estabilidad en 2026
        modelos_validos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        prioridad = ['models/gemini-1.5-flash', 'models/gemini-pro']
        for p in prioridad:
            if p in modelos_validos: return genai.GenerativeModel(p)
        return genai.GenerativeModel(modelos_validos[0])
    except:
        return genai.GenerativeModel('gemini-pro')

model = conectar_ia()

st.set_page_config(page_title="Public Go Elite v61", layout="wide")

# --- ESTILOS VISUALES PUBLIC GO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .analysis-box { background-color: #f8f9fa; padding: 18px; border-right: 5px solid #003b5c; border-radius: 5px; font-size: 0.95rem; line-height: 1.5; color: #333; }
    .news-item { border-bottom: 1px solid #f0f0f0; padding: 12px 0; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: 500; font-size: 1.05rem; }
    .ref-tag { color: #003b5c; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE INTELIGENCIA ---
def generar_analisis_categoria(cat, data, alcance):
    titulares_numerados = "".join([f"[{i}] {n['titulo'].split(' - ')[0]} " for i, n in enumerate(data, 1)])
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. Analiza estos hechos de {cat} en Venezuela ({alcance}) para hoy 27 de febrero 2026: {titulares_numerados}. 
    INSTRUCCIONES:
    1. PROHIBIDO: Introducciones, saludos o frases amables. 
    2. REFERENCIAS: Usa [n] para sustentar cada afirmación.
    3. ESTILO: Directo, tipo informe de inteligencia.
    4. RECOMENDACIÓN: Una frase final estratégica.
    """
    try:
        respuesta = model.generate_content(prompt).text
        # Limpieza de muletillas de la IA
        for frase in ["Estimados", "Como Directora", "He realizado", "Diagnóstico"]:
            respuesta = respuesta.replace(frase, "")
        return respuesta.strip()
    except:
        return "⚠️ La unidad de inteligencia está saturada. Por favor, espere 5 segundos y vuelva a intentar."

def buscar_rss(query, periodo_cod):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo_cod}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:7]:
            results.append({"titulo": item.title.get_text(), "link": item.link.get_text()})
    except: pass
    return results

# --- INTERFAZ ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("Tasa BCV", "417,35 Bs/$", "+0,8%")
    st.metric("PIB 2026", "10%", "Estable")

st.title("🛡️ Public Go: Strategic Insight Dashboard")
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Delcy OR Diosdado OR Fiscal General OR ministro OR nombramiento OR renuncia)',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR Repsol OR petróleo OR gas OR PDVSA OR energía)',
    "💰 ECONOMÍA": 'Venezuela (bcv OR dólar OR tasa OR pib OR crecimiento OR inversión)',
    "🌎 RELACIONES": 'Venezuela (Trump OR sanciones OR Washington)'
}

codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

# EL BOTÓN MAESTRO QUE RECUPERAMOS
if st.button("🚀 ANÁLISIS INFORMATIVO E INTELIGENCIA"):
    st.session_state['ver_noticias'] = True

if st.session_state.get('ver_noticias'):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss(q, codigos[alcance])
        
        if noticias:
            col_news, col_diag = st.columns([2, 1.2])
            with col_news:
                st.write("**📌 Noticias Recientes**")
                for j, n in enumerate(noticias, 1):
                    st.markdown(f"<div class='news-item'><span class='ref-tag'>[{j}]</span><a href='{n['link']}' target='_blank' class='news-link'>{n['titulo'].split(' - ')[0]}</a></div>", unsafe_allow_html=True)
            
            with col_diag:
                st.write("**🧠 Análisis de Inteligencia**")
                # Botón de inteligencia por sección para evitar el error 429
                if st.button(f"🔍 Generar Análisis {cat}", key=f"btn_{cat}"):
                    with st.spinner("Unidad de inteligencia analizando..."):
                        analisis = generar_analisis_categoria(cat, noticias, alcance)
                        st.markdown(f"<div class='analysis-box'>{analisis}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Sin novedades en {cat}.")

st.divider()
st.caption("Uso exclusivo Public Go Consultores.")
