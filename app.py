import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA ---
API_KEY = "TU_API_KEY_AQUI" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Public Go - Strategic Intelligence", layout="wide")

# --- DICCIONARIO ESTRATÉGICO DE PUBLIC GO ---
CATEGORIAS = {
    "🏛️ GOBIERNO Y TRANSICIÓN": ["fiscal", "devoe", "amnistía", "saab", "asamblea", "nombramiento", "renuncia", "justicia"],
    "🛢️ ENERGÍA Y PETRÓLEO": ["shell", "chevron", "repsol", "gas", "petróleo", "ofac", "licencia", "energía", "pdvsa"],
    "💰 ECONOMÍA Y NEGOCIOS": ["bcv", "dólar", "tasa", "pib", "crecimiento", "consumidor", "inversión", "arancel"],
    "🇺🇸 RELACIONES VENEZUELA-EE.UU.": ["trump", "estados unidos", "unión", "sanciones", "washington", "casa blanca", "socio"]
}

def clasificar_noticia(titulo):
    texto = titulo.lower()
    for cat, keywords in CATEGORIAS.items():
        if any(k in texto for k in keywords):
            return cat
    return "📑 OTRAS NOTICIAS"

def generar_analisis_respaldo(categoria):
    analisis = {
        "🏛️ GOBIERNO Y TRANSICIÓN": "La reestructuración judicial y las liberaciones por Amnistía buscan normalizar la institucionalidad para validar la transición internacionalmente.",
        "🛢️ ENERGÍA Y PETRÓLEO": "La reactivación de convenios con Shell y Repsol fundamenta la entrada de divisas y la estabilidad de las operaciones transnacionales.",
        "💰 ECONOMÍA Y NEGOCIOS": "El clima de optimismo y la estabilidad cambiaria sustentan la proyección de crecimiento del 10% del PIB para el cierre de 2026.",
        "🇺🇸 RELACIONES VENEZUELA-EE.UU.": "El reconocimiento de Venezuela como 'socio' por la administración Trump redefine el marco de sanciones y licencias operativas."
    }
    return analisis.get(categoria, "Análisis de entorno en desarrollo. Monitoreo preventivo activado.")

def buscar_inteligencia_completa(alcance):
    p_cod = "d" if alcance == "Hoy" else "w"
    # Query expandida para capturar todos tus pilares
    query = 'Venezuela (Fiscal OR "Larry Devoe" OR Shell OR Repsol OR PIB OR Trump OR "Ley de Amnistia") "2026"'
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{p_cod}"
    
    hallazgos = []
    vistos = set()
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:25]: # Aumentamos el rango de búsqueda
            link = item.link.get_text()
            if link not in vistos:
                titulo = item.title.get_text().split(" - ")[0]
                hallazgos.append({
                    "titulo": titulo,
                    "link": link,
                    "categoria": clasificar_noticia(titulo)
                })
                vistos.add(link)
    except: pass
    return hallazgos

# --- INTERFAZ ---
st.title("🛡️ Public Go: Dashboard Estratégico Multicapa")
periodo = st.sidebar.selectbox("Alcance:", ["Hoy", "Semana"])

if st.button("🚀 Actualizar Inteligencia"):
    data = buscar_inteligencia_completa(periodo)
    if data:
        df = pd.DataFrame(data)
        
        # Mostrar por cada categoría definida
        for cat in CATEGORIAS.keys():
            noticias_cat = df[df['categoria'] == cat]
            
            if not noticias_cat.empty:
                st.subheader(cat)
                # Intento de IA, si no, usa respaldo
                texto_bloque = " | ".join(noticias_cat['titulo'].tolist())
                try:
                    response = model.generate_content(f"Analiza estas noticias de {cat}: {texto_bloque}")
                    st.info(response.text)
                except:
                    st.info(generar_analisis_respaldo(cat))
                
                for _, row in noticias_cat.iterrows():
                    with st.expander(f"📌 {row['titulo']}"):
                        st.caption(f"[Fuente Oficial]({row['link']})")
                st.divider()
        
        # Otros Temas
        otros = df[df['categoria'] == "📑 OTRAS NOTICIAS"]
        if not otros.empty:
            with st.expander("📑 OTRAS NOTICIAS DETECTADAS"):
                for _, row in otros.iterrows():
                    st.write(f"• {row['titulo']} ([Fuente]({row['link']}))")
    else:
        st.warning("No se hallaron noticias frescas.")
