import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
from datetime import datetime

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Public Go Intelligence", layout="wide")

st.sidebar.image("https://via.placeholder.com/150?text=Public+Go", width=150) # Aquí irá tu logo
st.sidebar.title("Public Go Intelligence Hub")
periodo = st.sidebar.selectbox("Periodo de Análisis", ["Hoy", "Semana"])

# --- MOTOR DE ANÁLISIS PROFUNDO ---
def analizar_implicacion(titulo, texto):
    texto_min = (titulo + " " + texto).lower()
    
    if "fiscal" in texto_min or "devoe" in texto_min:
        return "🔄 IMPLICACIÓN: Reestructuración del sistema de justicia para validación internacional y posible revisión de expedientes críticos."
    if "shell" in texto_min or "gas" in texto_min:
        return "🛢️ IMPLICACIÓN: Apertura del sector gasífero a capital europeo; esto reduce la dependencia de ingresos por crudo pesado y estabiliza el flujo de caja estatal."
    if "amnistía" in texto_min:
        return "⚖️ IMPLICACIÓN: Reducción de la presión política interna y cumplimiento de hitos para el mantenimiento de licencias de la OFAC."
    if "trump" in texto_min or "socio" in texto_min:
        return "🇺🇸 IMPLICACIÓN: Cambio de doctrina hacia 'Realismo Económico'; se prioriza la estabilidad energética sobre la confrontación ideológica."
    
    return "📝 ANÁLISIS: Evolución de entorno bajo monitoreo preventivo."

# --- MOTOR DE BÚSQUEDA ---
def buscar_inteligencia():
    hallazgos = []
    queries = [
        'Venezuela ("Fiscal General" OR "Larry Devoe" OR "renuncia") "2026"',
        'Venezuela (Shell OR gas OR petróleo OR "Licencia") "2026"',
        'Venezuela (Amnistía OR "presos políticos") "2026"',
        'Venezuela (Trump OR "socio" OR "Estado de la Unión") "2026"'
    ]
    
    for q in queries:
        try:
            url = f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{'d' if periodo == 'Hoy' else 'w'}"
            r = requests.get(url, timeout=10)
            sopa = BeautifulSoup(r.text, 'xml')
            for item in sopa.find_all('item')[:5]:
                titulo = item.title.get_text().split(" - ")[0]
                link = item.link.get_text()
                
                # Extracción rápida
                try:
                    art = Article(link, language='es')
                    art.download(); art.parse()
                    resumen = art.text[:400]
                except:
                    resumen = "Ver detalle en fuente oficial."
                
                hallazgos.append({
                    "titulo": titulo,
                    "link": link,
                    "resumen": resumen,
                    "implicacion": analizar_implicacion(titulo, resumen)
                })
        except: continue
    return hallazgos

# --- INTERFAZ DE USUARIO ---
st.title("🛡️ Dashboard de Inteligencia Estratégica")
st.markdown(f"**Corte de información:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if st.button("Actualizar Inteligencia"):
    with st.spinner("Analizando coyuntura 2026..."):
        data = buscar_inteligencia()
        
        # Agrupar por importancia
        col1, col2 = st.columns(2)
        
        for i, noticia in enumerate(data):
            target_col = col1 if i % 2 == 0 else col2
            with target_col.expander(f"📌 {noticia['titulo'].upper()}", expanded=True):
                st.write(noticia['resumen'])
                st.info(noticia['implicacion'])
                st.caption(f"[Fuente Oficial]({noticia['link']})")

else:
    st.info("Haga clic en 'Actualizar Inteligencia' para obtener el análisis profundo del día.")
