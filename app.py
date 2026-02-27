import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# Debes poner tu API KEY en los "Secrets" de Streamlit o directamente aquí para probar
genai.configure(api_key="AIzaSyAwvvCJPRJ-d8B72oWb35tdLpAOEmhzZjU")
model = genai.GenerativeModel('gemini-pro')

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Public Go - AI Intelligence", layout="wide")

def realizar_analisis_ia(titulo, contenido, contexto_temporal):
    prompt = f"""
    Eres una IA experta en consultoría de asuntos públicos y estrategia en Venezuela.
    Analiza la siguiente noticia del {contexto_temporal} de febrero de 2026:
    
    TÍTULO: {titulo}
    CONTENIDO: {contenido}
    
    PROPORCIONA:
    1. Un análisis de impacto estratégico para empresas transnacionales.
    2. Implicaciones en la seguridad jurídica o flujo de caja.
    3. Una breve recomendación para la alta gerencia.
    Sé conciso, profesional y directo.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "El motor de IA no pudo procesar esta noticia en este momento."

# --- MOTOR DE BÚSQUEDA (BASADO EN TU v35.0) ---
def buscar_noticias_reales(periodo_op):
    hallazgos = []
    # Usamos tus palabras clave exactas de la v35.0
    queries = [
        'Venezuela (Shell OR Chevron OR Repsol OR "petróleo" OR "gas" OR "PDVSA" OR "Licencia") "2026"',
        'Venezuela ("Delcy" OR "Diosdado" OR "Fiscal General" OR "nombramiento" OR "renuncia") "2026"',
        'Venezuela (Amnistía OR "presos políticos") "2026"',
        'Venezuela (Trump OR "Washington" OR "Laura Dogu") "2026"'
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    vistos = set()
    periodo_cod = "d" if periodo_op == "Hoy" else "w"

    for q in queries:
        url = f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{periodo_cod}"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'xml')
            for item in soup.find_all('item')[:5]:
                link = item.link.get_text()
                if link not in vistos:
                    titulo = item.title.get_text().split(" - ")[0]
                    # Extraer contenido real de la noticia
                    try:
                        art = Article(link, language='es')
                        art.download(); art.parse()
                        cuerpo = art.text[:1000]
                    except: cuerpo = item.description.get_text()
                    
                    hallazgos.append({"titulo": titulo, "cuerpo": cuerpo, "link": link})
                    vistos.add(link)
        except: continue
    return hallazgos

# --- INTERFAZ ---
st.title("🛡️ Public Go: AI Strategy Dashboard")
st.sidebar.title("Filtros Estratégicos")
periodo = st.sidebar.radio("Alcance:", ["Hoy", "Semana"])

if st.button("🚀 Iniciar Escaneo e Inteligencia Artificial"):
    noticias = buscar_noticias_reales(periodo)
    
    if noticias:
        st.success(f"Analizando {len(noticias)} eventos detectados...")
        for n in noticias:
            with st.expander(f"📌 {n['titulo'].upper()}"):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**Resumen de la Noticia:**")
                    st.write(n['cuerpo'][:600] + "...")
                    st.caption(f"[Fuente]({n['link']})")
                with col2:
                    st.markdown("**🧠 ANÁLISIS DE INTELIGENCIA (IA):**")
                    # AQUÍ OCURRE LA MAGIA: La IA analiza LA NOTICIA REAL que encontró el scraping
                    analisis = realizar_analisis_ia(n['titulo'], n['cuerpo'], periodo)
                    st.info(analisis)
    else:
        st.warning("No se encontraron noticias nuevas con los parámetros de la v35.0.")
