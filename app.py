import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import os

# --- CONFIGURACIÓN DE IA ---
API_KEY = "AIzaSyAwvvCJPRJ-d8B72oWb35tdLpAOEmhzZjU" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- DISEÑO Y MARCA (ESTILO PUBLIC GO) ---
st.set_page_config(page_title="Public Go Intelligence", layout="wide")

st.markdown("""
    <style>
    /* Estética General */
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003049 !important; border-right: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* Títulos de Categoría */
    .cat-header {
        background-color: #003049;
        color: white;
        padding: 12px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: bold;
        font-size: 1.2rem;
        margin-top: 25px;
    }
    
    /* Caja de Análisis */
    .analysis-box {
        background-color: #f0f4f7;
        padding: 20px;
        border-radius: 0 0 8px 8px;
        border-left: 6px solid #003049;
        margin-bottom: 20px;
        font-style: italic;
    }

    /* Tarjetas de Noticias */
    .news-card {
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 10px;
        background-color: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CATEGORIZACIÓN ---
CATEGORIAS = {
    "🏛️ GOBIERNO Y TRANSICIÓN": ["fiscal", "devoe", "amnistía", "saab", "asamblea", "nombramiento", "renuncia", "justicia", "transición"],
    "🛢️ ENERGÍA Y PETRÓLEO": ["shell", "chevron", "repsol", "gas", "petróleo", "ofac", "licencia", "energía", "pdvsa", "crudo"],
    "💰 ECONOMÍA Y NEGOCIOS": ["bcv", "dólar", "tasa", "pib", "crecimiento", "consumidor", "inversión", "arancel", "pago", "banca"],
    "🇺🇸 RELACIONES VENEZUELA-EE.UU.": ["trump", "estados unidos", "unión", "sanciones", "washington", "casa blanca", "socio", "rubio"]
}

def obtener_analisis_ia(cat, titulares):
    prompt = f"Eres consultora de Public Go. Basado en estos titulares de {cat}: {titulares}, genera un análisis estratégico de 3 líneas sobre el impacto en Venezuela para este 26 de febrero de 2026."
    try:
        return model.generate_content(prompt).text
    except:
        return "Análisis en actualización. Revise los titulares para el contexto actual."

def ejecutar_radar(alcance):
    t_param = "d" if alcance == "Hoy" else "w"
    # Query balanceada para forzar resultados en todas las áreas
    query = 'Venezuela (Fiscal OR "Larry Devoe" OR Shell OR Repsol OR PIB OR "Amnistia" OR Trump) "2026"'
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{t_param}"
    
    results = []
    vistos = set()
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:30]: # Más profundidad
            link = item.link.get_text()
            title = item.title.get_text().split(" - ")[0]
            
            # Clasificación Precisa
            cat_final = "📑 OTROS TEMAS"
            for c, keywords in CATEGORIAS.items():
                if any(k in title.lower() for k in keywords):
                    cat_final = c
                    break
            
            if link not in vistos:
                results.append({"titulo": title, "link": link, "categoria": cat_final})
                vistos.add(link)
    except: pass
    return results

# --- INTERFAZ PRINCIPAL ---
with st.sidebar:
    if os.path.exists("logo_publicgo.png"):
        st.image("logo_publicgo.png")
    st.title("Public Go Elite")
    alcance = st.radio("Periodo de Análisis:", ["Hoy", "Semana"])
    st.divider()
    st.metric("PIB 2026 (Est.)", "10%", "+2.5%")
    st.metric("Riesgo País", "Moderado", "Estable")

st.markdown("<h1 style='color: #003049;'>🛡️ Intelligence Insight Hub</h1>", unsafe_allow_html=True)
st.write(f"Corte Informativo: **{datetime.now().strftime('%d/%m/%Y')}**")

if st.button("🚀 ACTUALIZAR REPORTE ESTRATÉGICO"):
    noticias = ejecutar_radar(alcance)
    
    if noticias:
        df = pd.DataFrame(noticias)
        
        # Despliegue por Bloques Estrictos
        for cat in CATEGORIAS.keys():
            subset = df[df['categoria'] == cat]
            
            # Crear el contenedor visual del bloque
            st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
            
            if not subset.empty:
                # Análisis de Bloque
                titulares_bloque = " | ".join(subset['titulo'].tolist())
                st.markdown(f"<div class='analysis-box'>{obtener_analisis_ia(cat, titulares_bloque, alcance)}</div>", unsafe_allow_html=True)
                
                # Lista de Noticias
                for _, row in subset.iterrows():
                    st.markdown(f"""
                        <div class='news-card'>
                            <strong>📌 {row['titulo']}</strong><br>
                            <a href='{row['link']}' target='_blank' style='color: #003049; font-size: 0.8rem;'>Ver Fuente Oficial</a>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='analysis-box'>No se detectaron movimientos críticos en este eje durante el periodo.</div>", unsafe_allow_html=True)
    else:
        st.warning("No se hallaron nuevas actualizaciones en los servidores de noticias.")
