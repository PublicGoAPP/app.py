import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN IA PRO (Solución al Error 404) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Eliminamos el prefijo 'models/' para evitar el error 404 en cuentas Pro
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de configuración: {e}")
        return None

model = conectar_ia()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go Intelligence Hub", layout="wide")

st.markdown("""
    <style>
    .main-title { color: #003b5c; font-weight: 800; font-size: 2.5rem; margin-bottom: 20px; }
    .cat-header { background-color: #003b5c; color: white; padding: 12px; border-radius: 5px; font-weight: bold; margin-top: 30px; }
    .risk-card { background-color: #fcfcfc; padding: 20px; border-radius: 10px; border-left: 12px solid #003b5c; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin-top: 10px; }
    .news-item { border-bottom: 1px solid #eee; padding: 10px 0; font-size: 0.95rem; line-height: 1.4; }
    .metric-text { font-size: 1.1rem; font-weight: bold; color: #003b5c; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE ANÁLISIS ESTRATÉGICO ---
def generar_analisis_robusto(cat, titulares):
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. 
    Analiza estos eventos en Venezuela para la categoría {cat}:
    {titulares}
    
    Responde estrictamente con esta estructura:
    1. 📊 ÍNDICE DE RIESGO POLÍTICO: (Escala 1-10 con breve justificación)
    2. 🛢️ IMPACTO EN ENERGÍA Y NEGOCIOS: (Análisis específico sobre crudo, gas, licencias o flujo de caja)
    3. 🛡️ RECOMENDACIÓN EJECUTIVA: (Acción sugerida para el cliente hoy)
    
    Usa un tono audaz y lenguaje de alta consultoría.
    """
    try:
        # Llamada directa al modelo corregido
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"⚠️ Error en el motor de IA: {str(e)}. Intenta refrescar la página."

# --- INTERFAZ SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Public Go")
    st.subheader("Intelligence Systems")
    periodo = st.radio("Ventana temporal:", ["Hoy", "Semana"])
    st.divider()
    st.metric("Tasa Oficial BCV", "417.36 Bs", "+0.79%")
    st.write("---")
    st.success("Conexión: Nivel de Pago 1")

# --- DASHBOARD PRINCIPAL ---
st.markdown("<h1 class='main-title'>Strategic Insight Dashboard</h1>", unsafe_allow_html=True)
st.write(f"Corte de inteligencia: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

CATEGORIAS = {
    "🏛️ GOBERNANZA Y PODER": 'Venezuela ("Larry Devoe" OR "Tarek William Saab" OR "Fiscalía")',
    "🛢️ ENERGÍA, GAS Y LICENCIAS": 'Venezuela (Shell OR Chevron OR PDVSA OR Licencia OR "44")',
    "💰 MACROECONOMÍA Y MERCADO": 'Venezuela (BCV OR "dólar" OR "inflación" OR "aranceles")'
}

if st.button("🚀 ACTUALIZAR Y GENERAR INTELIGENCIA"):
    for cat, query in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        
        # Búsqueda de noticias reales
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419"
        noticias_lista = []
        try:
            r = requests.get(url, timeout=10)
            sopa = BeautifulSoup(r.text, 'xml')
            for item in sopa.find_all('item')[:4]:
                titulo = item.title.get_text().split(" - ")[0]
                noticias_lista.append(f"• {titulo}")
        except: pass

        if noticias_lista:
            c1, c2 = st.columns([1, 1.2])
            with c1:
                st.markdown("**Eventos Clave Detectados:**")
                for n in noticias_lista:
                    st.markdown(f"<div class='news-item'>{n}</div>", unsafe_allow_html=True)
            with c2:
                with st.spinner(f"Analizando {cat}..."):
                    titulares_str = "\n".join(noticias_lista)
                    resultado = generar_analisis_robusto(cat, titulares_str)
                    st.markdown(f"<div class='risk-card'>{resultado}</div>", unsafe_allow_html=True)
        else:
            st.info("Sin eventos críticos detectados en los parámetros de búsqueda.")

st.divider()
st.caption("Public Go Elite v83.0 | Caracas, Venezuela")
