import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN SEGURA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error: Configure su API Key en los Secrets de Streamlit.")

st.set_page_config(page_title="Public Go Elite", layout="wide")

# --- DISEÑO CORPORATIVO ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 20px; }
    .analysis-box { background-color: #f0f7f9; padding: 15px; border-left: 6px solid #003b5c; margin-bottom: 20px; border-radius: 0 0 8px 8px; }
    .news-card { padding: 12px; border-bottom: 1px solid #e0e0e0; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- CATEGORÍAS Y KEYWORDS ---
CATEGORIAS = {
    "🏛️ GOBIERNO Y TRANSICIÓN": 'Venezuela ("Fiscal General" OR "Larry Devoe" OR "Amnistia" OR "Saab" OR "transicion")',
    "🛢️ ENERGÍA Y PETRÓLEO": 'Venezuela (Shell OR Repsol OR Chevron OR "PDVSA" OR "gas" OR "crudo" OR "exportacion")',
    "💰 ECONOMÍA Y NEGOCIOS": 'Venezuela (PIB OR "crecimiento economico" OR "BCV" OR "dolar" OR "inversion")',
    "🇺🇸 RELACIONES VENEZUELA-EE.UU.": 'Venezuela (Trump OR "Washington" OR "Casa Blanca" OR "Sanciones" OR "licencia")'
}

def generar_inteligencia(cat, titulares, periodo):
    prompt = f"Eres consultora senior en Public Go. Analiza estos hechos de {cat} del periodo {periodo}: {titulares}. Explica el impacto estratégico para este 26 de febrero de 2026. Sé muy específica con los riesgos y oportunidades."
    try:
        return model.generate_content(prompt).text
    except: return "Generando análisis de respaldo..."

def buscar_noticias_profundas(periodo_label):
    t_param = "d" if periodo_label == "Hoy" else "w"
    results = []
    vistos = set()
    
    # FORZAMOS UNA BÚSQUEDA POR CADA CATEGORÍA
    for cat, query in CATEGORIAS.items():
        full_query = f'{query} "2026"'
        url = f"https://news.google.com/rss/search?q={full_query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{t_param}"
        
        try:
            r = requests.get(url, timeout=12)
            soup = BeautifulSoup(r.text, 'xml')
            items = soup.find_all('item')
            # Si es SEMANA, traemos más (15), si es HOY, menos (5)
            limite = 15 if periodo_label == "Semana" else 5
            
            for item in items[:limite]:
                title = item.title.get_text().split(" - ")[0]
                link = item.link.get_text()
                if link not in vistos:
                    results.append({"titulo": title, "link": link, "categoria": cat})
                    vistos.add(link)
        except: continue
    return results

# --- INTERFAZ ---
with st.sidebar:
    st.markdown("### 🛡️ Radar Estratégico")
    alcance = st.radio("Filtro de Tiempo:", ["Hoy", "Semana"])
    st.divider()
    st.metric("PIB 2026 (Est.)", "10%", "+2.5%")
    st.metric("Riesgo País", "Moderado", "Estable")

st.markdown("<h1 style='color: #003b5c;'>Public Go: Intelligence Insight Hub</h1>", unsafe_allow_html=True)
st.write(f"Análisis generado el: **{datetime.now().strftime('%d/%m/%Y')}**")

if st.button("🚀 ACTUALIZAR INTELIGENCIA"):
    noticias = buscar_noticias_profundas(alcance)
    if noticias:
        df = pd.DataFrame(noticias)
        for cat in CATEGORIAS.keys():
            subset = df[df['categoria'] == cat]
            st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
            
            if not subset.empty:
                titulares = " | ".join(subset['titulo'].tolist())
                st.markdown(f"<div class='analysis-box'>{generar_inteligencia(cat, titulares, alcance)}</div>", unsafe_allow_html=True)
                for _, row in subset.iterrows():
                    st.markdown(f"<div class='news-card'>📌 {row['titulo']} <br> <a href='{row['link']}' target='_blank' style='color:#003b5c; font-size:0.85rem;'>Consultar Fuente</a></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='analysis-box'>No se detectaron hitos específicos en este eje durante las últimas horas.</div>", unsafe_allow_html=True)
    else:
        st.warning("No se hallaron resultados. Intenta ampliar el alcance a 'Semana'.")
