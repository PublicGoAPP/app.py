import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# --- CONFIGURACIÓN DE IA PRO (Nivel 1) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en Secrets.")
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de configuración: {e}")
        return None

model = conectar_ia()

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Public Go Intelligence Hub", layout="wide")

# Estilos de Consultoría Premium
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 12px; border-radius: 5px; font-weight: bold; margin-top: 25px; }
    .risk-box { padding: 18px; border-radius: 8px; margin-top: 10px; border-left: 10px solid #003b5c; background-color: #fcfcfc; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .news-item { border-bottom: 1px solid #f0f0f0; padding: 10px 0; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE ANÁLISIS ESTRATÉGICO ---
def generar_analisis_riesgo(cat, data, alcance):
    titulares = "".join([f"- {n['titulo']} " for n in data])
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. 
    Analiza estos hechos en Venezuela ({alcance}) para la categoría {cat}:
    {titulares}
    
    Estructura tu respuesta:
    1. 🛡️ NIVEL DE RIESGO: (Bajo/Medio/Alto)
    2. 💡 IMPLICACIÓN ESTRATÉGICA: Impacto en gobernanza o clima de negocios.
    3. 🎯 RECOMENDACIÓN CLAVE: Acción sugerida para el cliente.
    
    Usa un tono audaz, ejecutivo y profesional.
    """
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"⚠️ Error en análisis: El sistema está sincronizando tu nivel de pago. Reintenta en breve."

# --- MOTOR DE BÚSQUEDA ---
@st.cache_data(ttl=600)
def buscar_rss(query, periodo):
    time_code = "1d" if periodo == "Hoy" else "7d"
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{time_code}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:5]:
            results.append({"titulo": item.title.get_text().split(" - ")[0], "link": item.link.get_text()})
    except: pass
    return results

# --- SIDEBAR PROFESIONAL ---
with st.sidebar:
    st.title("🛡️ Public Go")
    st.markdown("### Estrategia e Inteligencia")
    alcance = st.radio("Ventana de Monitoreo:", ["Hoy", "Semana"])
    st.divider()
    st.metric("Tasa Oficial BCV", "417.36 Bs", "+0.79%")
    st.caption("Corte: 27 Feb 2026")
    st.write("---")
    st.info("Cuenta: Producción Nivel 1")

# --- DASHBOARD PRINCIPAL ---
st.markdown("<h1 style='color: #003b5c;'>Strategic Insight Dashboard</h1>", unsafe_allow_html=True)
st.write(f"Inteligencia en tiempo real para la toma de decisiones.")

CATEGORIAS = {
    "🏛️ PODER PÚBLICO": 'Venezuela ("Larry Devoe" OR "Tarek William Saab" OR "Fiscalía")',
    "🛢️ ENERGÍA Y SANCIONES": 'Venezuela (Chevron OR Shell OR PDVSA OR Licencia OR gas)',
    "💰 MACROECONOMÍA": 'Venezuela (BCV OR inflación OR aranceles OR dólar)',
    "🌎 GEOPOLÍTICA": 'Venezuela (Trump OR Marco Rubio OR Washington OR sanciones)'
}

if st.button("🚀 INICIAR MONITOREO DE ALTA VELOCIDAD"):
    st.session_state['ready'] = True

if st.session_state.get('ready'):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss(q, alcance)
        
        if noticias:
            c1, c2 = st.columns([1.5, 1.5])
            with c1:
                st.markdown("#### Eventos Detectados")
                for n in noticias:
                    st.markdown(f"<div class='news-item'>• <a href='{n['link']}' target='_blank' style='color:#003b5c; text-decoration:none;'>{n['titulo']}</a></div>", unsafe_allow_html=True)
            with c2:
                if st.button(f"🧠 Analizar {cat}", key=cat):
                    with st.spinner("Analizando implicaciones..."):
                        analisis = generar_analisis_riesgo(cat, noticias, alcance)
                        st.markdown(f"<div class='risk-box'>{analisis}</div>", unsafe_allow_html=True)
        else:
            st.info(f"No se detectaron cambios críticos en {cat} en este periodo.")

st.divider()
st.caption("Public Go Elite v81.0 | Confidencial")
