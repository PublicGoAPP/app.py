import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import time

# --- CONFIGURACIÓN DE IA OPTIMIZADA ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave.")
        return None
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Usamos configuración de generación para mayor velocidad
    config = genai.types.GenerationConfig(temperature=0.3, top_p=0.8)
    return genai.GenerativeModel('gemini-1.5-flash', generation_config=config)

model = conectar_ia()

st.set_page_config(page_title="Public Go Elite v68", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; }
    .analysis-box { background-color: #f8f9fa; padding: 15px; border-left: 5px solid #003b5c; border-radius: 5px; color: #333; }
    .news-item { border-bottom: 1px solid #f0f0f0; padding: 8px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
def calcular_variacion_real(alcance):
    tasa_actual = 417.3579
    cierres = {"Hoy": 414.0594, "Semana": 412.2030, "Mes": 401.3055}
    previo = cierres.get(alcance)
    var = ((tasa_actual - previo) / previo) * 100
    return tasa_actual, var

def generar_analisis_lite(cat, data, alcance):
    titulares = " ".join([f"[{i}] {n['titulo'][:80]}" for i, n in enumerate(data, 1)])
    # Prompt ultra-optimizado para no sacrificar calidad pero sí peso
    prompt = f"Analista Senior Public Go. Venezuela ({alcance}). Hechos: {titulares}. Tarea: Resumen ejecutivo impacto/tendencia. Usa [n]. Termina con recomendación breve."
    
    for intento in range(3):
        try:
            res = model.generate_content(prompt)
            return res.text.strip()
        except Exception as e:
            if "429" in str(e):
                time.sleep(3 * (intento + 1))
                continue
            return "⚠️ Servidor saturado. Intente en 10s."
    return "⚠️ Límite de cuota excedido. Por favor, espere un minuto."

@st.cache_data(ttl=600)
def buscar_rss(query, periodo):
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{periodo}&hl=es-419&gl=VE&ceid=VE:es-419"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        return [{"titulo": i.title.text, "link": i.link.text} for i in soup.find_all('item')[:6]]
    except: return []

# --- INTERFAZ ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    tasa, var = calcular_variacion_real(alcance)
    st.metric("Tasa BCV", f"{tasa:.4f}", f"{var:+.2f}%")
    st.metric("EMBI", "18,450 bps", "-50 bps", delta_color="inverse")

st.title("🛡️ Strategic Insight Dashboard")
st.write(f"Corte: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Delcy OR Diosdado OR nombramiento)',
    "🛢️ ENERGÍA": 'Venezuela (Chevron OR PDVSA OR gas)',
    "💰 ECONOMÍA": 'Venezuela (bcv OR dólar OR tasa OR inversión)',
    "🌎 RELACIONES": 'Venezuela (Trump OR sanciones OR Washington)'
}

if 'analisis_mem' not in st.session_state:
    st.session_state['analisis_mem'] = {}

if st.button("🚀 CARGAR INTELIGENCIA"):
    st.session_state['ready'] = True
    st.session_state['analisis_mem'] = {}

if st.session_state.get('ready'):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss(q, "1d" if alcance=="Hoy" else ("7d" if alcance=="Semana" else "30d"))
        
        if noticias:
            c1, c2 = st.columns([1.8, 1.2])
            with c1:
                for j, n in enumerate(noticias, 1):
                    st.markdown(f"<div class='news-item'>[{j}] <a href='{n['link']}' target='_blank' style='color:#003b5c; text-decoration:none;'>{n['titulo'].split(' - ')[0]}</a></div>", unsafe_allow_html=True)
            with c2:
                if st.button(f"🧠 Analizar {cat}", key=f"btn_{cat}"):
                    with st.spinner("Procesando..."):
                        st.session_state['analisis_mem'][cat] = generar_analisis_lite(cat, noticias, alcance)
                
                if cat in st.session_state['analisis_mem']:
                    st.markdown(f"<div class='analysis-box'>{st.session_state['analisis_mem'][cat]}</div>", unsafe_allow_html=True)

st.divider()
st.caption("Public Go Elite v68.0 | Optimización de cuota activada.")
