import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN DE IA ---
# Reemplaza con tu clave real o configúrala en los Secrets de Streamlit
API_KEY = "AIzaSyAwvvCJPRJ-d8B72oWb35tdLpAOEmhzZjU" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Public Go AI Intelligence", layout="wide")

def analizar_con_ia(titulo, texto, periodo):
    prompt = f"""
    Actúa como un consultor senior de Public Go en Venezuela. 
    Analiza esta noticia del {periodo} de febrero de 2026 para una empresa como Empire Keeway:
    Título: {titulo}
    Contenido: {texto}
    
    Proporciona:
    1. Impacto estratégico (Jurídico/Económico).
    2. Riesgos u Oportunidades detectadas.
    3. Recomendación ejecutiva breve.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Análisis no disponible en este momento."

# --- MOTOR DE BÚSQUEDA (BASADO EN TU v35.0) ---
def buscar_noticias(alcance):
    resultados = []
    vistos = set()
    queries = [
        'Venezuela (Shell OR Chevron OR "PDVSA" OR "gas") "2026"',
        'Venezuela ("Fiscal General" OR "Larry Devoe" OR "renuncia") "2026"',
        'Venezuela ("Ley de Amnistia" OR "presos politicos") "2026"',
        'Venezuela (Trump OR "Washington") "2026"'
    ]
    
    t_param = "d" if alcance == "Hoy" else "w"
    headers = {"User-Agent": "Mozilla/5.0"}

    for q in queries:
        url = f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl=es-419&gl=VE&ceid=VE:es-419&tbs=qdr:{t_param}"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'xml')
            for item in soup.find_all('item')[:5]:
                link = item.link.get_text()
                if link not in vistos:
                    titulo = item.title.get_text().split(" - ")[0]
                    try:
                        art = Article(link, language='es')
                        art.download(); art.parse()
                        cuerpo = art.text[:1000]
                    except: cuerpo = "Contenido extraído de la descripción del feed."
                    
                    resultados.append({"titulo": titulo, "cuerpo": cuerpo, "link": link})
                    vistos.add(link)
        except: continue
    return resultados

# --- INTERFAZ ---
st.title("🛡️ Public Go: AI Strategy Hub")
periodo_op = st.sidebar.radio("Alcance:", ["Hoy", "Semana"])

if st.button("🚀 Generar Inteligencia en Tiempo Real"):
    with st.spinner("La IA está analizando los eventos de 2026..."):
        noticias = buscar_noticias(periodo_op)
        if noticias:
            for n in noticias:
                with st.expander(f"📌 {n['titulo'].upper()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(n['cuerpo'][:500] + "...")
                        st.caption(f"[Fuente]({n['link']})")
                    with col2:
                        st.info(analizar_con_ia(n['titulo'], n['cuerpo'], periodo_op))
        else:
            st.warning("No se hallaron noticias frescas. Intenta con el alcance 'Semana'.")
