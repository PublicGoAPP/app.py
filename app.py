import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN IA PRO (Solución Definitiva al 404) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        # Configuramos para usar la versión de producción, no la beta
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # En cuentas de pago, el nombre del modelo es simplemente este:
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error crítico de configuración: {e}")
        return None

model = conectar_ia()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go Intelligence Hub", layout="wide")

st.markdown("""
    <style>
    .main-title { color: #003b5c; font-weight: 800; font-size: 2.8rem; margin-bottom: 5px; }
    .cat-header { background-color: #003b5c; color: white; padding: 12px; border-radius: 5px; font-weight: bold; margin-top: 30px; border-bottom: 4px solid #f1c40f; }
    .risk-card { background-color: #fcfcfc; padding: 20px; border-radius: 10px; border-left: 12px solid #003b5c; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .news-box { background-color: #ffffff; padding: 15px; border: 1px solid #eee; border-radius: 8px; margin-bottom: 10px; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: bold; font-size: 1rem; }
    .news-link:hover { text-decoration: underline; color: #f1c40f; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE ANÁLISIS ESTRATÉGICO ---
def generar_inteligencia_public_go(cat, titulares, periodo):
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. 
    Analiza estos eventos en Venezuela para la categoría {cat} durante el periodo de {periodo}:
    {titulares}
    
    ESTRUCTURA OBLIGATORIA:
    1. 📊 ÍNDICE DE RIESGO POLÍTICO: (Escala 1-10 y justificación estratégica)
    2. 🛢️ IMPACTO EN ENERGÍA Y NEGOCIOS: (Análisis profundo sobre crudo, gas, licencias u operatividad)
    3. 🛡️ RECOMENDACIÓN EJECUTIVA: (Acción sugerida para el cliente)
    
    Tono: Alta consultoría, audaz y pragmático.
    """
    try:
        # Usamos la llamada estándar que soporta el Nivel 1 de pago
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"⚠️ Error en el motor de IA: {str(e)}. Por favor, verifica los logs de la consola."

# --- SIDEBAR ESTRATÉGICO ---
with st.sidebar:
    st.title("🛡️ Public Go")
    st.subheader("Intelligence Systems")
    # Restauramos la opción de Mes
    alcance = st.selectbox("Ventana de Análisis:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("Tasa Oficial BCV", "417.36 Bs", "+0.79%")
    st.write("---")
    st.success("SISTEMA: Nivel 1 (Producción)")
    st.caption("Corte: 27 Feb 2026")

# --- CUERPO DEL DASHBOARD ---
st.markdown("<h1 class='main-title'>Strategic Insight Dashboard</h1>", unsafe_allow_html=True)
st.write(f"Inteligencia Estratégica | Venezuela - {datetime.now().strftime('%d/%m/%Y %H:%M')}")

CATEGORIAS = {
    "🏛️ GOBERNANZA Y PODER": 'Venezuela ("Larry Devoe" OR "Tarek William Saab" OR "Fiscalía")',
    "🛢️ ENERGÍA, GAS Y LICENCIAS": 'Venezuela (Shell OR Chevron OR PDVSA OR Licencia OR "44")',
    "💰 MACROECONOMÍA Y MERCADO": 'Venezuela (BCV OR "dólar" OR "inflación" OR "aranceles")'
}

codigos_tiempo = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if st.button("🚀 GENERAR REPORTE DE INTELIGENCIA"):
    for cat, query in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        
        # Búsqueda de noticias con enlaces
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{codigos_tiempo[alcance]}"
        hallazgos = []
        try:
            r = requests.get(url, timeout=12)
            sopa = BeautifulSoup(r.text, 'xml')
            for item in sopa.find_all('item')[:4]:
                hallazgos.append({
                    "titulo": item.title.get_text().split(" - ")[0],
                    "link": item.link.get_text()
                })
        except: pass

        if hallazgos:
            col1, col2 = st.columns([1, 1.2])
            with col1:
                st.write("**Eventos Detectados:**")
                titulares_texto = ""
                for h in hallazgos:
                    st.markdown(f"""
                        <div class='news-box'>
                            <a class='news-link' href='{h['link']}' target='_blank'>{h['titulo']}</a>
                        </div>
                    """, unsafe_allow_html=True)
                    titulares_texto += f"- {h['titulo']}\n"
            with col2:
                with st.spinner(f"IA analizando impacto en {cat}..."):
                    analisis = generar_inteligencia_public_go(cat, titulares_texto, alcance)
                    st.markdown(f"<div class='risk-card'>{analisis}</div>", unsafe_allow_html=True)
        else:
            st.info(f"No se detectaron cambios críticos en {cat} durante el último {alcance.lower()}.")

st.divider()
st.caption("Public Go Elite v84.0 | Uso estrictamente confidencial.")
