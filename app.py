import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA PRO ---
def inicializar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("🚨 Falta la clave API en los Secrets de Streamlit.")
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos gemini-1.5-flash: es el más estable para cuentas Nivel 1
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error al configurar Google AI: {e}")
        return None

model = inicializar_ia()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go Intelligence", layout="wide")

st.markdown("""
    <style>
    .main-header { color: #003b5c; font-size: 2.5rem; font-weight: 800; }
    .report-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 8px solid #003b5c; margin-bottom: 15px; }
    .stButton>button { background-color: #003b5c; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE BÚSQUEDA ---
def buscar_noticias():
    # Buscamos los temas que definimos: Larry Devoe, Fiscalía, Gas y Sanciones
    query = 'Venezuela ("Larry Devoe" OR "Fiscalía" OR "Shell" OR "Trump") when:1d'
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419"
    
    noticias = []
    try:
        r = requests.get(url, timeout=10)
        sopa = BeautifulSoup(r.text, 'xml')
        for item in sopa.find_all('item')[:6]:
            noticias.append({
                "titulo": item.title.get_text().split(" - ")[0],
                "link": item.link.get_text(),
                "fecha": item.pubDate.get_text()[:16]
            })
    except:
        st.error("Error al conectar con el servidor de noticias.")
    return noticias

# --- MOTOR DE ANÁLISIS ---
def analizar_con_ia(titulo):
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. 
    Analiza este titular de hoy en Venezuela: "{titulo}"
    Proporciona:
    1. IMPLICACIÓN: Qué significa esto para el sector privado y la gobernanza.
    2. RIESGO: Nivel de riesgo (Bajo/Medio/Alto).
    Responde de forma ejecutiva y profesional en español.
    """
    try:
        res = model.generate_content(prompt)
        return res.text
    except:
        return "⚠️ La IA está procesando el cambio de nivel de pago. Reintenta en unos minutos."

# --- INTERFAZ ---
st.markdown("<h1 class='main-header'>🛡️ Public Go Intelligence Hub</h1>", unsafe_allow_html=True)
st.write(f"Corte de análisis: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if st.button("🚀 ACTUALIZAR INTELIGENCIA ESTRATÉGICA"):
    noticias = buscar_noticias()
    if noticias:
        col1, col2 = st.columns(2)
        for i, n in enumerate(noticias):
            with (col1 if i % 2 == 0 else col2):
                st.markdown(f"<div class='report-card'><strong>{n['titulo']}</strong><br><small>{n['fecha']}</small></div>", unsafe_allow_html=True)
                with st.expander("👁️ Ver Análisis de Riesgo"):
                    with st.spinner("IA Generando Insight..."):
                        analisis = analizar_con_ia(n['titulo'])
                        st.write(analisis)
                        st.caption(f"[Leer noticia completa]({n['link']})")
    else:
        st.warning("No se encontraron noticias críticas en las últimas 24 horas.")

st.sidebar.title("Configuración")
st.sidebar.info("Modo: Pago Nivel 1 (Producción)")
st.sidebar.write("---")
st.sidebar.caption("© 2026 Public Go Consultores")
