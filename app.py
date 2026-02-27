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

st.set_page_config(page_title="Public Go Elite v55.6", layout="wide")

# --- ESTILOS VISUALES REFINADOS ---
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

# --- FUNCIONES ESTRATÉGICAS ---
def generar_analisis_inteligente(cat, data, alcance):
    if not model: return "Error de conexión con el motor de IA."
    
    # Creamos una lista numerada para que la IA pueda referenciar
    titulares_numerados = ""
    for i, n in enumerate(data, 1):
        titulares_numerados += f"[{i}] {n['titulo'].split(' - ')[0]} "

    prompt = f"""
    Eres la Directora de Estrategia de Public Go. Analiza estos hechos de {cat} en Venezuela ({alcance}) para hoy 27 de febrero 2026: {titulares_numerados}. 
    
    INSTRUCCIONES CRÍTICAS:
    1. PROHIBIDO: No uses introducciones, ni saludos, ni frases como 'Estimados colegas' o 'He realizado un análisis'.
    2. REFERENCIAS: Cada vez que menciones un hecho o hagas una afirmación, DEBES incluir el número de la fuente entre corchetes, ej: [1] o [1, 3].
    3. ESTRUCTURA: Ve directo al grano. Identifica la tendencia y el impacto. 
    4. CUANTITATIVO: Solo si hay cifras relevantes en los titulares, analízalas.
    5. Recomendación estratégica final sin preámbulos.
    """
    try:
        # Limpiamos posibles introducciones que la IA genere por inercia
        respuesta = model.generate_content(prompt).text
        # Filtro extra de seguridad por si la IA ignora el prompt
        frases_a_borrar = ["Estimados colegas", "Como Directora", "análisis profundo", "Diagnóstico Cualitativo Profundo"]
        for frase in frases_a_borrar:
            respuesta = respuesta.replace(frase, "")
        return respuesta.strip()
    except:
        return "El análisis estratégico está siendo procesado por la unidad de inteligencia..."

def buscar_rss_profundo(query, periodo_cod):
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
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR Repsol OR petróleo OR gas OR PDVSA OR energía OR Licencia)',
    "💰 ECONOMÍA": 'Venezuela (bcv OR dólar OR tasa OR pib OR crecimiento OR consumidor OR inversión OR arancel)',
    "🌎 RELACIONES": 'Venezuela (Trump OR Marco Rubio OR Washintong OR sanciones OR Laura Dogu)'
}

codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if st.button("🚀 ANÁLISIS INFORMATIVO E INTELIGENCIA"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss_profundo(q, codigos[alcance])
        
        if noticias:
            col_news, col_diag = st.columns([2, 1.2])
            
            with col_news:
                st.write("**📌 Noticias Recientes**")
                for i, n in enumerate(noticias, 1):
                    st.markdown(f"""
                        <div class='news-item'>
                            <span class='ref-tag'>[{i}]</span>
                            <a href='{n['link']}' target='_blank' class='news-link'>
                                {n['titulo'].split(' - ')[0]}
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
            
            with col_diag:
                # 2. Nombre cambiado a Análisis de Inteligencia
                st.write("**🧠 Análisis de Inteligencia**")
                st.markdown(f"<div class='analysis-box'>{generar_analisis_inteligente(cat, noticias, alcance)}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Sin novedades significativas en el eje de {cat}.")

st.divider()
st.caption("Uso exclusivo Public Go Consultores.")
