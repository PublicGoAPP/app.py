import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import time

# --- CONFIGURACIÓN DE IA (REPARADA PARA CUENTA PRO) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en Secrets.")
        return None
    try:
        # Forzamos el uso de la versión estable (v1) en lugar de la beta
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # IMPORTANTE: En cuentas Pro, se usa el nombre del modelo sin prefijos
        return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de configuración: {e}")
        return None

# Inicialización correcta
model = conectar_ia()

st.set_page_config(page_title="Public Go Elite v74", layout="wide")

# --- ESTILOS VISUALES CORPORATIVOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 25px; text-transform: uppercase; }
    .risk-high { border-left: 8px solid #d9534f; background-color: #fff5f5; padding: 15px; border-radius: 5px; color: #333; }
    .risk-med { border-left: 8px solid #f0ad4e; background-color: #fff9f0; padding: 15px; border-radius: 5px; color: #333; }
    .news-item { border-bottom: 1px solid #f0f0f0; padding: 12px 0; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: 500; font-size: 1.05rem; }
    </style>
    """, unsafe_allow_html=True)

# --- CAPA DE INTELIGENCIA DE RIESGO ---
def generar_analisis_riesgo(cat, data, alcance):
    if not model:
        return "⚠️ IA no configurada. Revisa los Secrets."
    
    titulares = "".join([f"[{i}] {n['titulo'].split(' - ')[0]} " for i, n in enumerate(data, 1)])
    prompt = f"""
    Actúa como Directora de Riesgo de Public Go. 
    Analiza estos hechos en Venezuela ({alcance}): {titulares}
    Estructura tu respuesta así:
    1. NIVEL DE RIESGO: (Bajo/Medio/Alto)
    2. ANÁLISIS: Breve impacto en el clima de negocios.
    3. RECOMENDACIÓN: Acción inmediata para clientes corporativos.
    Usa [n] para referencias. Sin saludos.
    """
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"⚠️ Error de conexión: {str(e)}"

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

# --- SIDEBAR & CÁLCULOS ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("Tasa BCV", "417.35 Bs", "+0.79%")
    st.metric("EMBI (Riesgo País)", "18,450 bps", "-50 bps", delta_color="inverse")

# --- CUERPO PRINCIPAL ---
st.title("🛡️ Strategic Insight Dashboard")
st.subheader("Monitoreo de Riesgo Político y Económico")

CATEGORIAS = {
    "🏛️ GOBIERNO & PODER": 'Venezuela (Larry Devoe OR Tarek William Saab OR Fiscal OR Asamblea Nacional)',
    "🛢️ ENERGÍA & LICENCIAS": 'Venezuela (Shell OR Chevron OR PDVSA OR Licencia OR sanciones)',
    "💰 ECONOMÍA & CONSUMO": 'Venezuela (bcv OR dólar OR inflación OR canasta)',
    "🌎 RELACIONES EXTERNAS": 'Venezuela (Trump OR Marco Rubio OR Washington OR diplomacia)'
}
codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if st.button("🚀 GENERAR REPORTE DE INTELIGENCIA"):
    st.session_state['ver'] = True

if st.session_state.get('ver'):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss(q, codigos[alcance])
        
        if noticias:
            c1, c2 = st.columns([1.8, 1.2])
            with c1:
                st.write("**📌 Eventos Detectados**")
                for j, n in enumerate(noticias, 1):
                    st.markdown(f"<div class='news-item'>[{j}] <a href='{n['link']}' target='_blank' class='news-link'>{n['titulo'].split(' - ')[0]}</a></div>", unsafe_allow_html=True)
            with c2:
                st.write("**🧠 Análisis de Riesgo**")
                # El botón de análisis por categoría
                if st.button(f"🔍 Evaluar Riesgo {cat}", key=cat):
                    with st.spinner("Calculando impacto..."):
                        analisis = generar_analisis_riesgo(cat, noticias, alcance)
                        clase = "risk-high" if "ALTO" in analisis.upper() else "risk-med"
                        st.markdown(f"<div class='{clase}'>{analisis}</div>", unsafe_allow_html=True)

st.divider()
st.caption(f"Public Go Elite v74.0 | Corte: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
