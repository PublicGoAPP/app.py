import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import os

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# Recuerda poner tu API KEY aquí
API_KEY = "TU_API_KEY_AQUI" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Public Go - Strategic Intelligence", 
    page_icon="🛡️",
    layout="wide"
)

# --- DISEÑO DE MARCA (COLORES PUBLIC GO) ---
# Azul oscuro: #003049 | Blanco: #FFFFFF
st.markdown("""
    <style>
    /* Fondo y Barra Lateral */
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #003049; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Títulos de Bloque */
    .section-header {
        color: #003049;
        border-bottom: 3px solid #003049;
        padding-bottom: 10px;
        margin-top: 30px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    /* Caja de Análisis IA */
    .stChatMessage {
        background-color: #e8f1f5;
        border-radius: 15px;
        border-left: 5px solid #003049;
    }
    
    /* Botón Principal */
    .stButton>button {
        background-color: #003049;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INTELIGENCIA ---
CATEGORIAS = {
    "🏛️ GOBIERNO Y TRANSICIÓN": ["fiscal", "devoe", "amnistía", "saab", "asamblea", "nombramiento", "renuncia", "justicia"],
    "🛢️ ENERGÍA Y PETRÓLEO": ["shell", "chevron", "repsol", "gas", "petróleo", "ofac", "licencia", "energía", "pdvsa"],
    "💰 ECONOMÍA Y NEGOCIOS": ["bcv", "dólar", "tasa", "pib", "crecimiento", "consumidor", "inversión", "arancel"],
    "🇺🇸 RELACIONES VENEZUELA-EE.UU.": ["trump", "estados unidos", "unión", "sanciones", "washington", "casa blanca", "socio"]
}

def generar_analisis_ia_bloque(categoria, noticias, periodo):
    prompt = f"Como consultora de Public Go, analiza estos titulares de {categoria}: {noticias}. Da una conclusión de 3 líneas para inversionistas en Venezuela (Feb 2026)."
    try:
        return model.generate_content(prompt).text
    except:
        return "Análisis estratégico en revisión. Consulte los indicadores del periodo."

def buscar_inteligencia(alcance):
    p_cod = "d" if alcance == "Hoy" else "w"
    query = 'Venezuela (Fiscal OR Devoe OR Shell OR Repsol OR PIB OR "Amnistia") "2026"'
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{p_cod}"
    
    hallazgos = []
    vistos = set()
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:20]:
            link = item.link.get_text()
            titulo = item.title.get_text().split(" - ")[0]
            cat_asignada = "📑 OTROS"
            for c, keywords in CATEGORIAS.items():
                if any(k in titulo.lower() for k in keywords):
                    cat_asignada = c
                    break
            
            if link not in vistos:
                hallazgos.append({"titulo": titulo, "link": link, "categoria": cat_asignada})
                vistos.add(link)
    except: pass
    return hallazgos

# --- INTERFAZ ---
with st.sidebar:
    if os.path.exists("logo_publicgo.png"):
        st.image("logo_publicgo.png", width=200)
    else:
        st.markdown("<h2 style='color:white;'>Public Go</h2>", unsafe_allow_html=True)
    
    st.divider()
    periodo = st.selectbox("Rango de Análisis:", ["Hoy", "Semana"])
    st.metric("PIB Proyectado 2026", "10%", "+2.5%")
    st.metric("Riesgo País", "Moderado", "Tendencia ↓")

st.markdown(f"<h1 style='color: #003049;'>🛡️ Intelligence Insight Hub</h1>", unsafe_allow_html=True)
st.write(f"Corte de información: **{datetime.now().strftime('%d/%m/%Y')}**")

if st.button("🚀 ACTUALIZAR RADAR ESTRATÉGICO"):
    data = buscar_inteligencia(periodo)
    if data:
        df = pd.DataFrame(data)
        
        # Gráfico de Tendencias
        st.write("### Tendencia Informativa del Periodo")
        st.bar_chart(df['categoria'].value_counts())

        # Despliegue por Bloques
        for cat in CATEGORIAS.keys():
            noticias_cat = df[df['categoria'] == cat]
            if not noticias_cat.empty:
                st.markdown(f"<div class='section-header'>{cat}</div>", unsafe_allow_html=True)
                
                # Análisis IA
                texto_titulares = " | ".join(noticias_cat['titulo'].tolist())
                with st.chat_message("assistant", avatar="🛡️"):
                    st.write(generar_analisis_ia_bloque(cat, texto_titulares, periodo))
                
                # Lista de Noticias
                for _, row in noticias_cat.iterrows():
                    st.markdown(f"📌 **{row['titulo']}** \n[Ver Fuente]({row['link']})")
                st.divider()
    else:
        st.warning("No se hallaron nuevas actualizaciones.")
