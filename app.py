import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import time

# --- CONFIGURACIÓN DE IA ULTRA-RESILIENTE (v73.0) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en Secrets.")
        return None
    
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Lista exhaustiva de todas las formas posibles de llamar al modelo
    nombres_posibles = [
        'gemini-1.5-flash',
        'models/gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'models/gemini-1.5-flash-latest',
        'gemini-pro' # Último recurso si Flash falla
    ]
    
    for nombre in nombres_posibles:
        try:
            # Intentamos inicializar
            modelo_prueba = genai.GenerativeModel(nombre)
            # Intentamos una respuesta ultra corta para validar que el modelo existe y responde
            modelo_prueba.generate_content("ok", generation_config={"max_output_tokens": 1})
            return modelo_prueba
        except:
            continue
    return None

model = conectar_ia()

st.set_page_config(page_title="Public Go Elite v73", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .analysis-box { background-color: #f8f9fa; padding: 18px; border-right: 5px solid #003b5c; border-radius: 5px; font-size: 0.95rem; line-height: 1.5; color: #333; }
    .news-item { border-bottom: 1px solid #f0f0f0; padding: 12px 0; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: 500; font-size: 1.05rem; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE CÁLCULO ---
def calcular_variacion_real(alcance):
    tasa_actual = 417.3579
    cierres = {"Hoy": 414.0594, "Semana": 412.2030, "Mes": 401.3055}
    precio_previo = cierres.get(alcance, 414.0594)
    variacion_pct = ((tasa_actual - precio_previo) / precio_previo) * 100
    return tasa_actual, variacion_pct

# --- ANÁLISIS ---
def generar_analisis_categoria(cat, data, alcance):
    if not model:
        return "⚠️ Error crítico: Google no reconoce ningún modelo disponible para esta clave."
    
    titulares = "".join([f"[{i}] {n['titulo'].split(' - ')[0]} " for i, n in enumerate(data, 1)])
    prompt = f"Analista Senior Public Go. Venezuela ({alcance}). Hechos: {titulares}. Tarea: Impacto y recomendación estratégica. Sin saludos. Usa [n]."
    
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"⚠️ Error en la generación: {str(e)}"

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

# --- INTERFAZ ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro:", ["Hoy", "Semana", "Mes"])
    st.divider()
    tasa, var = calcular_variacion_real(alcance)
    st.metric("Tasa BCV", f"{tasa:.4f} Bs", f"{var:+.2f}%")

st.title("🛡️ Public Go: Strategic Insight Dashboard")
st.write(f"Corte: **27/02/2026**")

if model is None:
    st.error("❌ Fallo total de conexión con los modelos de Google. Por favor, verifica que la clave en Secrets sea correcta y no tenga espacios.")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Larry Devoe OR Tarek William Saab OR Delcy Rodriguez)',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR PDVSA OR gas)',
    "💰 ECONOMÍA": 'Venezuela (bcv OR dólar OR tasa OR pib)',
    "🌎 RELACIONES": 'Venezuela (Trump OR sanciones OR Washington)'
}
codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if 'ver' not in st.session_state: st.session_state['ver'] = False
if 'analisis' not in st.session_state: st.session_state['analisis'] = {}

if st.button("🚀 INICIAR MONITOREO"):
    st.session_state['ver'] = True
    st.session_state['analisis'] = {}

if st.session_state['ver']:
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss(q, codigos[alcance])
        if noticias:
            c1, c2 = st.columns([2, 1.2])
            with c1:
                for j, n in enumerate(noticias, 1):
                    st.markdown(f"[{j}] <a href='{n['link']}' target='_blank' class='news-link'>{n['titulo'].split(' - ')[0]}</a>", unsafe_allow_html=True)
            with c2:
                if st.button(f"🔍 Analizar {cat}", key=cat):
                    with st.spinner("Analizando..."):
                        st.session_state['analisis'][cat] = generar_analisis_categoria(cat, noticias, alcance)
                if cat in st.session_state['analisis']:
                    st.markdown(f"<div class='analysis-box'>{st.session_state['analisis'][cat]}</div>", unsafe_allow_html=True)

st.divider()
st.caption("Public Go Elite v73.0 | Protocolo de Inferencia Directa Activado.")
