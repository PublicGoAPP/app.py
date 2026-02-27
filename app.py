import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN IA PRO (Solución al Error 404 de Pago) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # En cuentas Pro, se usa el nombre directo sin prefijos beta
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de configuración: {e}")
        return None

model = conectar_ia()

# --- CONFIGURACIÓN VISUAL PUBLIC GO ---
st.set_page_config(page_title="Public Go Intelligence Hub", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .main-title { color: #003b5c; font-weight: 800; font-size: 2.8rem; }
    .cat-header { background-color: #003b5c; color: white; padding: 12px; border-radius: 5px; font-weight: bold; margin-top: 30px; border-left: 10px solid #f1c40f; }
    .risk-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 12px solid #003b5c; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .news-box { border-bottom: 1px solid #eee; padding: 12px 0; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: bold; }
    .news-link:hover { color: #f1c40f; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE INTELIGENCIA ESTRATÉGICA ---
def generar_inteligencia(cat, titulares, periodo):
    prompt = f"""
    Eres la Directora de Estrategia de Public Go. Analiza estos eventos en Venezuela ({periodo}) para {cat}:
    {titulares}
    
    ESTRUCTURA DE RESPUESTA:
    1. 📊 ÍNDICE DE RIESGO POLÍTICO: (Escala 1-10 y por qué)
    2. 🛢️ IMPACTO EN ENERGÍA Y NEGOCIOS: (Análisis sobre crudo, gas, licencias o flujo de caja)
    3. 🛡️ RECOMENDACIÓN EJECUTIVA: (Acción sugerida para el cliente hoy)
    """
    try:
        # Forzamos la llamada de producción para evitar el error 404
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"⚠️ Error de conexión Pro: {str(e)}. Intenta reiniciar la App."

# --- MOTOR DE BÚSQUEDA LIMPIO (Sin Repeticiones) ---
def buscar_noticias_limpias(query, periodo):
    time_code = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}[periodo]
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{time_code}"
    
    hallazgos = []
    vistos = set() # Para evitar noticias repetidas
    try:
        r = requests.get(url, timeout=12)
        sopa = BeautifulSoup(r.text, 'xml')
        for item in sopa.find_all('item'):
            titulo = item.title.get_text().split(" - ")[0]
            # Limpieza de duplicados por palabras clave en el título
            token = titulo[:30].lower() 
            if token not in vistos and len(hallazgos) < 4:
                hallazgos.append({"titulo": titulo, "link": item.link.get_text()})
                vistos.add(token)
    except: pass
    return hallazgos

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.selectbox("Ventana de Análisis:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("Tasa Oficial BCV", "417.36 Bs", "+0.79%")
    st.success("SISTEMA: Nivel 1 (Producción)")

# --- DASHBOARD ---
st.markdown("<h1 class='main-title'>Strategic Insight Dashboard</h1>", unsafe_allow_html=True)
st.write(f"Inteligencia Estratégica | Venezuela - {datetime.now().strftime('%d/%m/%Y %H:%M')}")

CATEGORIAS = {
    "🏛️ GOBERNANZA Y PODER": 'Venezuela ("Larry Devoe" OR "Tarek William Saab" OR "Fiscalía")',
    "🛢️ ENERGÍA Y LICENCIAS": 'Venezuela (Chevron OR Shell OR PDVSA OR Licencia OR gas)',
    "💰 MACRO Y MERCADO": 'Venezuela (BCV OR "dólar" OR "inflación" OR "aranceles")'
}

if st.button("🚀 GENERAR INTELIGENCIA INTEGRAL"):
    for cat, query in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_noticias_limpias(query, alcance)
        
        if noticias:
            c1, c2 = st.columns([1, 1.2])
            with c1:
                st.write("**Eventos Detectados:**")
                titulares_texto = ""
                for n in noticias:
                    st.markdown(f"<div class='news-box'><a class='news-link' href='{n['link']}' target='_blank'>{n['titulo']}</a></div>", unsafe_allow_html=True)
                    titulares_texto += f"- {n['titulo']}\n"
            with c2:
                with st.spinner(f"IA analizando {cat}..."):
                    analisis = generar_inteligencia(cat, titulares_texto, alcance)
                    st.markdown(f"<div class='risk-card'>{analisis}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Sin cambios críticos detectados en {cat} para este periodo.")

st.divider()
st.caption("Public Go Elite v85.0 | Confidencial")
