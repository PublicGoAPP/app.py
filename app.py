import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import os

# --- SEGURIDAD: CARGA DESDE SECRETS ---
try:
    # Busca la clave en la "caja fuerte" de Streamlit
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error de Configuración: Verifique la API Key en los Secrets de Streamlit.")

# --- DISEÑO Y MARCA (ESTILO PUBLIC GO) ---
st.set_page_config(page_title="Public Go Intelligence", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header {
        background-color: #003b5c;
        color: white;
        padding: 12px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: bold;
        margin-top: 25px;
    }
    .analysis-box {
        background-color: #f0f7f9;
        padding: 20px;
        border-radius: 0 0 8px 8px;
        border-left: 6px solid #003b5c;
        margin-bottom: 20px;
    }
    .news-card {
        padding: 15px;
        border-bottom: 1px solid #e0e0e0;
        background-color: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CATEGORÍAS ---
CATEGORIAS = {
    "🏛️ GOBIERNO Y TRANSICIÓN": ["fiscal", "devoe", "amnistía", "saab", "nombramiento", "renuncia", "justicia"],
    "🛢️ ENERGÍA Y PETRÓLEO": ["shell", "chevron", "repsol", "gas", "petróleo", "ofac", "licencia", "pdvsa"],
    "💰 ECONOMÍA Y NEGOCIOS": ["bcv", "dólar", "tasa", "pib", "crecimiento", "inversión"],
    "🇺🇸 RELACIONES VENEZUELA-EE.UU.": ["trump", "estados unidos", "sanciones", "washington", "casa blanca"]
}

# CORRECCIÓN DEL ERROR: Ahora acepta exactamente 3 parámetros
def obtener_analisis_ia(cat, titulares, periodo):
    prompt = f"Como consultora de Public Go, analiza estos titulares de {cat} del {periodo} de febrero 2026: {titulares}. Da una conclusión estratégica de 3 líneas."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Análisis estratégico en actualización técnica."

def ejecutar_radar(alcance):
    t_param = "d" if alcance == "Hoy" else "w"
    query = 'Venezuela (Fiscal OR "Larry Devoe" OR Shell OR Repsol OR PIB OR "Amnistia" OR Trump) "2026"'
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{t_param}"
    
    results = []
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:25]:
            title = item.title.get_text().split(" - ")[0]
            cat_final = "📑 OTROS TEMAS"
            for c, keywords in CATEGORIAS.items():
                if any(k in title.lower() for k in keywords):
                    cat_final = c
                    break
            results.append({"titulo": title, "link": item.link.get_text(), "categoria": cat_final})
    except: pass
    return results

# --- INTERFAZ ---
with st.sidebar:
    st.markdown("### 🛡️ Radar Public Go")
    alcance = st.radio("Periodo:", ["Hoy", "Semana"])
    st.divider()
    st.metric("PIB 2026 (Est.)", "10%", "+2.5%")
    st.metric("Riesgo País", "Moderado", "Estable")

st.markdown("<h1 style='color: #003b5c;'>Public Go: Intelligence Hub</h1>", unsafe_allow_html=True)
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}**")

if st.button("🚀 ACTUALIZAR REPORTE"):
    noticias = ejecutar_radar(alcance)
    if noticias:
        df = pd.DataFrame(noticias)
        for cat in CATEGORIAS.keys():
            subset = df[df['categoria'] == cat]
            st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
            if not subset.empty:
                titulares = " | ".join(subset['titulo'].tolist())
                # AQUÍ SE SOLUCIONA EL ERROR: Enviamos los 3 datos correctos
                st.markdown(f"<div class='analysis-box'>{obtener_analisis_ia(cat, titulares, alcance)}</div>", unsafe_allow_html=True)
                for _, row in subset.iterrows():
                    st.markdown(f"<div class='news-card'>📌 {row['titulo']} <br> <a href='{row['link']}' target='_blank' style='color:#003b5c; font-size:0.8rem;'>Ver Fuente Oficial</a></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='analysis-box'>No se detectaron movimientos críticos en este eje.</div>", unsafe_allow_html=True)
    else:
        st.warning("No se hallaron noticias nuevas.")
