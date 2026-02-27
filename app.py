import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import time

# --- CONFIGURACIÓN DE IA CORREGIDA (v71.0) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en Secrets.")
        return None
    
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Intentamos la conexión con el nombre de modelo actualizado
    try:
        # Usamos el nombre completo y estable para evitar el error 404
        return genai.GenerativeModel('models/gemini-1.5-flash-latest')
    except:
        # Backup en caso de que la librería prefiera el nombre corto
        return genai.GenerativeModel('gemini-1.5-flash')

model = conectar_ia()

st.set_page_config(page_title="Public Go Elite v71", layout="wide")

# --- ESTILOS VISUALES ---
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

# --- MOTOR DE CÁLCULO ---
def calcular_variacion_real(alcance):
    tasa_actual = 417.3579
    cierres = {"Hoy": 414.0594, "Semana": 412.2030, "Mes": 401.3055}
    precio_previo = cierres.get(alcance, 414.0594)
    variacion_pct = ((tasa_actual - precio_previo) / precio_previo) * 100
    return tasa_actual, variacion_pct

# --- FUNCIONES DE BÚSQUEDA Y ANÁLISIS ---
def generar_analisis_categoria(cat, data, alcance):
    titulares = "".join([f"[{i}] {n['titulo'].split(' - ')[0]} " for i, n in enumerate(data, 1)])
    prompt = f"Eres Directora de Public Go. Analiza {cat} en Venezuela ({alcance}): {titulares}. Sin saludos. Usa [n]. Recomendación final."
    try:
        # Pequeña pausa de seguridad para evitar saturación
        time.sleep(1)
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"⚠️ No se pudo generar el análisis: {str(e)}"

@st.cache_data(ttl=600)
def buscar_rss(query, periodo):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:7]:
            results.append({"titulo": item.title.get_text(), "link": item.link.get_text()})
    except: pass
    return results

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    tasa, variacion = calcular_variacion_real(alcance)
    st.metric(label="Tasa Oficial BCV", value=f"{tasa:.4f} Bs", delta=f"{variacion:+.2f}%")
    st.metric("Riesgo País (EMBI)", "18,450 bps", "-50 bps", delta_color="inverse")

# --- CUERPO PRINCIPAL ---
st.title("🛡️ Public Go: Strategic Insight Dashboard")
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Delcy OR Diosdado OR Fiscal General OR ministro OR nombramiento OR renuncia)',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR PDVSA OR gas OR Licencia)',
    "💰 ECONOMÍA": 'Venezuela (bcv OR dólar OR tasa OR pib OR crecimiento OR inversión)',
    "🌎 RELACIONES": 'Venezuela (Trump OR Marco Rubio OR Washington OR sanciones)'
}
codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if 'analisis' not in st.session_state:
    st.session_state['analisis'] = {}

if st.button("🚀 INICIAR MONITOREO E INTELIGENCIA"):
    st.session_state['ver_noticias'] = True
    st.session_state['analisis'] = {} 

if st.session_state.get('ver_noticias'):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss(q, codigos[alcance])
        
        if noticias:
            col_n, col_d = st.columns([2, 1.2])
            with col_n:
                st.write("**📌 Noticias**")
                for j, n in enumerate(noticias, 1):
                    st.markdown(f"<div class='news-item'><span class='ref-tag'>[{j}]</span><a href='{n['link']}' target='_blank' class='news-link'>{n['titulo'].split(' - ')[0]}</a></div>", unsafe_allow_html=True)
            
            with col_d:
                st.write("**🧠 Análisis de Inteligencia**")
                if st.button(f"🔍 Analizar {cat}", key=f"btn_{cat}"):
                    with st.spinner("Procesando..."):
                        res = generar_analisis_categoria(cat, noticias, alcance)
                        st.session_state['analisis'][cat] = res
                
                if cat in st.session_state['analisis']:
                    st.markdown(f"<div class='analysis-box'>{st.session_state['analisis'][cat]}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Sin novedades en {cat}.")

st.divider()
st.caption("Public Go Elite v71.0 | Conexión a modelos de última generación.")
