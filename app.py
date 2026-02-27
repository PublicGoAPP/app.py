import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# Reemplaza con tu clave o usa st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key="AIzaSyAwvvCJPRJ-d8B72oWb35tdLpAOEmhzZjU")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go - Strategic Intelligence", layout="wide")

CATEGORIAS = {
    "🏛️ GOBIERNO Y TRANSICIÓN": ["fiscal", "devoe", "amnistía", "saab", "asamblea", "nombramiento", "renuncia", "justicia"],
    "🛢️ ENERGÍA Y PETRÓLEO": ["shell", "chevron", "repsol", "gas", "petróleo", "ofac", "licencia", "energía", "pdvsa"],
    "💰 ECONOMÍA Y NEGOCIOS": ["bcv", "dólar", "tasa", "pib", "crecimiento", "consumidor", "inversión", "arancel"],
    "🇺🇸 RELACIONES VENEZUELA-EE.UU.": ["trump", "estados unidos", "unión", "sanciones", "washington", "casa blanca", "socio"]
}

def generar_analisis_ia_bloque(categoria, noticias_texto, periodo):
    prompt = f"""
    Eres una consultora de Public Go. Analiza estas noticias de la categoría {categoria} para el periodo {periodo}:
    {noticias_texto}
    
    Proporciona una síntesis estratégica de 3 líneas que explique el impacto para una multinacional en Venezuela este 2026.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Análisis automático no disponible. Revise los titulares individuales."

def clasificar_noticia(titulo, cuerpo):
    texto = (titulo + " " + cuerpo).lower()
    for cat, keywords in CATEGORIAS.items():
        if any(k in texto for k in keywords):
            return cat
    return "📑 OTROS TEMAS"

def buscar_inteligencia(periodo_label):
    p_cod = "d" if periodo_label == "Hoy" else "w"
    all_keywords = [k for sublist in CATEGORIAS.values() for k in sublist]
    query_base = f"Venezuela ({' OR '.join(all_keywords[:12])}) 2026"
    url = f"https://news.google.com/rss/search?q={query_base.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{p_cod}"
    
    hallazgos = []
    vistos = set()
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        items = soup.find_all('item')
        limite = 20 if periodo_label == "Semana" else 8
        
        for item in items[:limite]:
            link = item.link.get_text()
            if link not in vistos:
                titulo = item.title.get_text().split(" - ")[0]
                try:
                    art = Article(link, language='es')
                    art.download(); art.parse()
                    cuerpo = art.text[:800]
                except: cuerpo = item.description.get_text()
                
                hallazgos.append({
                    "titulo": titulo, 
                    "cuerpo": cuerpo, 
                    "link": link, 
                    "categoria": clasificar_noticia(titulo, cuerpo)
                })
                vistos.add(link)
    except: pass
    return hallazgos

# --- INTERFAZ ---
st.title("🛡️ Public Go: Dashboard Estratégico Categorizado")
periodo = st.sidebar.selectbox("Alcance:", ["Hoy", "Semana"])

if st.button("🚀 Actualizar Inteligencia"):
    data = buscar_inteligencia(periodo)
    
    if data:
        df = pd.DataFrame(data)
        
        # Resumen de Tendencia
        conteo = df['categoria'].value_counts()
        st.metric("Categoría con Mayor Actividad", conteo.idxmax(), f"{conteo.max()} noticias")
        
        for cat in CATEGORIAS.keys():
            noticias_cat = df[df['categoria'] == cat]
            
            if not noticias_cat.empty:
                st.subheader(cat)
                
                # Análisis profundo con IA del bloque
                texto_bloque = " | ".join(noticias_cat['titulo'].tolist())
                with st.chat_message("assistant"):
                    st.write(generar_analisis_ia_bloque(cat, texto_bloque, periodo))
                
                # Noticias individuales
                for _, row in noticias_cat.iterrows():
                    with st.expander(f"📌 {row['titulo']}"):
                        st.write(row['cuerpo'])
                        st.caption(f"[Fuente Oficial]({row['link']})")
                st.divider()
    else:
        st.warning("No se hallaron noticias para este periodo.")
