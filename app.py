import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from collections import Counter
import pandas as pd
import re
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Public Go Analytics", layout="wide")

def extraer_cifras(texto):
    # Busca porcentajes, montos en $ o Bs.
    patron = r'(\d+(?:\.\d+)?\s?%|\$\s?\d+(?:\.\d+)?|Bs\.\s?\d+(?:\.\d+)?)'
    return re.findall(patron, texto)

def buscar_inteligencia_avanzada(periodo_label):
    periodo_cod = "d" if periodo_label == "Hoy" else "w"
    hallazgos = []
    texto_total = ""
    vistos = set()
    
    queries = [
        'Venezuela economia 2026 "PIB"',
        'Venezuela "Larry Devoe" Fiscal',
        'Venezuela "Shell" "Repsol" gas',
        'Venezuela "Amnistia" Foro Penal'
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}

    for q in queries:
        url = f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{periodo_cod}"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'xml')
            items = soup.find_all('item')
            
            # Si es SEMANA, tomamos más resultados (hasta 20) que si es HOY (5)
            limite = 20 if periodo_label == "Semana" else 5
            
            for item in items[:limite]:
                link = item.link.get_text()
                if link not in vistos:
                    titulo = item.title.get_text().split(" - ")[0]
                    try:
                        art = Article(link, language='es')
                        art.download(); art.parse()
                        cuerpo = art.text
                        resumen = art.summary if art.summary else cuerpo[:500]
                    except:
                        cuerpo = item.description.get_text()
                        resumen = cuerpo[:500]
                    
                    hallazgos.append({
                        "titulo": titulo,
                        "resumen": resumen,
                        "link": link,
                        "cifras": extraer_cifras(cuerpo)
                    })
                    texto_total += " " + titulo + " " + resumen
                    vistos.add(link)
        except: continue
    return hallazgos, texto_total

# --- INTERFAZ ---
st.title("🛡️ Public Go: Analytics & Insight Hub")
periodo = st.sidebar.selectbox("Rango de Monitoreo:", ["Hoy", "Semana"])

if st.button("🚀 Ejecutar Análisis"):
    with st.spinner(f"Analizando datos de la {periodo.lower()}..."):
        data, gran_texto = buscar_inteligencia_avanzada(periodo)
        
        if data:
            # --- SECCIÓN DE INDICADORES ---
            st.header("📊 Indicadores del Periodo")
            c1, c2 = st.columns([1, 2])
            
            # 1. Temas más mencionados (Análisis de palabras)
            palabras = re.findall(r'\w{5,}', gran_texto.lower())
            comunes = Counter(palabras).most_common(10)
            df_temas = pd.DataFrame(comunes, columns=['Tema', 'Menciones'])
            
            with c1:
                st.write("**Top Temas Detectados**")
                st.dataframe(df_temas, hide_index=True)
            
            # 2. Cifras clave detectadas
            todas_cifras = [c for h in data for c in h['cifras']]
            if todas_cifras:
                with c2:
                    st.write("**Cifras y Datos Económicos Extraídos**")
                    st.write(", ".join(list(set(todas_cifras))[:15]))

            st.divider()

            # --- SECCIÓN DE NOTICIAS CON ANÁLISIS ---
            st.header("🔍 Hallazgos Detallados")
            for n in data:
                with st.expander(f"📌 {n['titulo'].upper()}"):
                    st.write(n['resumen'])
                    if n['cifras']:
                        st.info(f"📊 Datos clave en esta noticia: {', '.join(n['cifras'])}")
                    st.caption(f"[Fuente]({n['link']})")
        else:
            st.warning("No se encontraron datos suficientes.")

st.sidebar.markdown("---")
st.sidebar.caption("v43.0 - Public Go Consulting")
