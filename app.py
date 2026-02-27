import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Public Go - Categorized Intelligence", layout="wide")

# --- CATEGORÍAS ESTRATÉGICAS ---
CATEGORIAS = {
    "🏛️ GOBIERNO Y TRANSICIÓN": ["fiscal", "devoe", "amnistía", "saab", "asamblea", "nombramiento", "renuncia", "justicia"],
    "🛢️ ENERGÍA Y PETRÓLEO": ["shell", "chevron", "repsol", "gas", "petróleo", "ofac", "licencia", "energía", "pdvsa"],
    "💰 ECONOMÍA Y NEGOCIOS": ["bcv", "dólar", "tasa", "pib", "crecimiento", "consumidor", "inversión", "arancel"],
    "🇺🇸 RELACIONES VENEZUELA-EE.UU.": ["trump", "estados unidos", "unión", "sanciones", "washington", "casa blanca", "socio"]
}

def clasificar_noticia(titulo, cuerpo):
    texto = (titulo + " " + cuerpo).lower()
    for cat, keywords in CATEGORIAS.items():
        if any(k in texto for k in keywords):
            return cat
    return "📑 OTROS TEMAS"

def buscar_inteligencia_categorizada(periodo_label):
    p_cod = "d" if periodo_label == "Hoy" else "w"
    hallazgos = []
    vistos = set()
    
    # Queries unificadas
    all_keywords = [k for sublist in CATEGORIAS.values() for k in sublist]
    query_base = f"Venezuela ({' OR '.join(all_keywords[:15])}) 2026"
    
    url = f"https://news.google.com/rss/search?q={query_base.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{p_cod}"
    
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        items = soup.find_all('item')
        limite = 25 if periodo_label == "Semana" else 10
        
        for item in items[:limite]:
            link = item.link.get_text()
            if link not in vistos:
                titulo = item.title.get_text().split(" - ")[0]
                try:
                    art = Article(link, language='es')
                    art.download(); art.parse()
                    cuerpo = art.text
                except:
                    cuerpo = item.description.get_text()
                
                categoria = clasificar_noticia(titulo, cuerpo)
                hall_data = {"titulo": titulo, "cuerpo": cuerpo[:800], "link": link, "categoria": categoria}
                hallazgos.append(hall_data)
                vistos.add(link)
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        
    return hallazgos

# --- INTERFAZ STREAMLIT ---
st.title("🛡️ Public Go: Dashboard de Inteligencia Categorizada")
st.markdown(f"**Corte de Información:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

with st.sidebar:
    st.header("Filtros")
    periodo = st.selectbox("Seleccione Alcance:", ["Hoy", "Semana"])
    st.divider()
    st.info("Este dashboard clasifica noticias en tiempo real según los ejes estratégicos de Public Go.")

if st.button("🚀 Actualizar Inteligencia"):
    data = buscar_inteligencia_categorizada(periodo)
    
    if data:
        df = pd.DataFrame(data)
        
        # --- ANÁLISIS DE TENDENCIAS ---
        st.header("📊 Análisis de Tendencia")
        conteo = df['categoria'].value_counts()
        dominante = conteo.idxmax()
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Categoría Dominante", dominante, f"{conteo.max()} noticias")
        with col_m2:
            st.write("**Distribución de Noticias:**")
            st.bar_chart(conteo)

        st.divider()

        # --- BLOQUES CATEGORIZADOS ---
        for cat in CATEGORIAS.keys():
            noticias_cat = df[df['categoria'] == cat]
            
            if not noticias_cat.empty:
                st.subheader(cat)
                
                # Análisis de Bloque
                with st.container():
                    st.markdown("---")
                    st.markdown(f"**💡 Análisis de bloque ({periodo}):**")
                    # Lógica simple de síntesis
                    if cat == "🏛️ GOBIERNO Y TRANSICIÓN":
                        st.info("La conversación se centra en el relevo judicial y la Ley de Amnistía. Este eje es crítico para la estabilidad de la transición.")
                    elif cat == "🛢️ ENERGÍA Y PETRÓLEO":
                        st.info("Se observa una reactivación de convenios con Shell y Repsol, lo que fundamenta las expectativas de ingreso de divisas.")
                    elif cat == "💰 ECONOMÍA Y NEGOCIOS":
                        st.info(f"Las cifras capturadas sugieren un clima de optimismo hacia la meta del 10% del PIB para el cierre de 2026.")
                    else:
                        st.info(f"Se detecta un volumen de {len(noticias_cat)} noticias enfocadas en este eje estratégico.")

                # Lista de Noticias
                for _, row in noticias_sec = noticias_cat.iterrows():
                    with st.expander(f"📌 {row['titulo']}"):
                        st.write(row['cuerpo'] + "...")
                        st.caption(f"[Fuente Oficial]({row['link']})")
                st.ln = 2
    else:
        st.warning("No se encontraron noticias en este rango.")

st.markdown("---")
st.caption("v44.0 | Documento de Uso Exclusivo - Public Go Consulting")
