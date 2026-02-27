import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN IA PRO ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    return genai.GenerativeModel('gemini-1.5-flash')

model = conectar_ia()

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Public Go Intelligence", layout="wide")

st.markdown("""
    <style>
    .main-title { color: #003b5c; font-weight: 800; font-size: 2.5rem; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; margin: 20px 0 10px 0; font-weight: bold; }
    .risk-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 10px solid #003b5c; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .metric-box { text-align: center; padding: 10px; background: #ebf3f7; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ANÁLISIS ---
def analizar_impacto(categoria, titulares):
    prompt = f"""
    Actúa como Directora de Inteligencia de Public Go.
    Analiza estos hechos de hoy en Venezuela para la categoría {categoria}:
    {titulares}
    
    Estructura tu respuesta:
    1. 📊 ÍNDICE DE RIESGO: (Escala 1-10 y por qué)
    2. 🛢️ IMPACTO EN ENERGÍA/NEGOCIOS: Análisis específico sobre crudo, gas o licencias si aplica.
    3. 🛡️ RECOMENDACIÓN ESTRATÉGICA: Acción inmediata para el cliente.
    """
    try:
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"⚠️ Error de respuesta: {str(e)}. Verifica que la facturación en Google Cloud esté activa para el proyecto PGAPP."

# --- INTERFAZ ---
st.markdown("<h1 class='main-title'>🛡️ Public Go Intelligence</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.title("Panel de Control")
    alcance = st.radio("Periodo:", ["Hoy", "Semana"])
    st.divider()
    st.metric("Tasa BCV", "417.36 Bs", "+0.79%")
    st.info("Nivel 1 de Pago Activo")

CATEGORIAS = {
    "🏛️ GOBERNANZA Y PODER": 'Venezuela ("Larry Devoe" OR "Fiscalía" OR "Tarek")',
    "🛢️ CRUDO, GAS Y LICENCIAS": 'Venezuela (Chevron OR Shell OR PDVSA OR Licencia OR "44")',
    "💰 MACRO Y MERCADO": 'Venezuela (BCV OR dólar OR inflación OR aranceles)'
}

if st.button("🚀 ACTUALIZAR Y ANALIZAR TODO"):
    for cat, query in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        
        # Búsqueda de noticias
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419"
        noticias = []
        try:
            r = requests.get(url, timeout=10)
            sopa = BeautifulSoup(r.text, 'xml')
            for item in sopa.find_all('item')[:3]:
                noticias.append(f"- {item.title.get_text()}")
        except: pass

        if noticias:
            col_not, col_an = st.columns([1, 1.2])
            with col_not:
                st.write("**Eventos Clave:**")
                for n in noticias:
                    st.write(n)
            with col_an:
                with st.spinner("IA Calculando Índice de Riesgo..."):
                    resumen_titulares = "\n".join(noticias)
                    analisis = analizar_impacto(cat, resumen_titulares)
                    st.markdown(f"<div class='risk-card'>{analisis}</div>", unsafe_allow_html=True)
        else:
            st.write("No se detectaron cambios críticos hoy.")

st.divider()
st.caption("Public Go Elite v82.0 | Conexión Pro")
