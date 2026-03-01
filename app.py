import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import urllib.parse

# --- CONFIGURACIÓN DE IA ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave en Secrets.")
        return None
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    return genai.GenerativeModel('gemini-1.5-flash')

model = conectar_ia()

st.set_page_config(page_title="Public Go Elite v70", layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 12px; border-radius: 5px; font-weight: bold; margin-top: 25px; text-transform: uppercase; letter-spacing: 1px; }
    .analysis-box { background-color: #f8f9fa; padding: 20px; border-left: 5px solid #003b5c; border-radius: 5px; font-size: 0.95rem; line-height: 1.6; color: #333; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .news-item { border-bottom: 1px solid #f0f0f0; padding: 12px 0; transition: 0.3s; }
    .news-item:hover { background-color: #fcfcfc; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: 600; font-size: 1rem; }
    .ref-tag { color: #d4af37; font-weight: bold; margin-right: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def crear_link_whatsapp(texto):
    texto_enc = urllib.parse.quote(f"🛡️ *PUBLIC GO - INTELLIGENCE REPORT*\n\n{texto}")
    return f"https://wa.me/?text={texto_enc}"

# --- LÓGICA DE BÚSQUEDA ---
@st.cache_data(ttl=600)
def buscar_rss(query, periodo):
    # Fusión de tus medios indicados + los sugeridos
    fuentes = (
        'site:bancaynegocios.com OR site:petroguia.com OR site:hispanopost.com OR '
        'site:efectococuyo.com OR site:elestimulo.com OR site:bloomberglinea.com OR '
        'site:finanzasdigital.com'
    )
    full_query = f"{query} ({fuentes})"
    
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(full_query)}+when:{periodo}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    try:
        r = requests.get(url, timeout=12)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:8]:
            results.append({"titulo": item.title.get_text(), "link": item.link.get_text()})
    except: pass
    return results

def generar_analisis_categoria(cat, data, alcance):
    titulares = "".join([f"[{i}] {n['titulo'].split(' - ')[0]} " for i, n in enumerate(data, 1)])
    prompt = (
        f"Eres la Directora de Public Go. Analiza la situación de {cat} en Venezuela para el periodo {alcance}. "
        f"Datos: {titulares}. Redacta un párrafo ejecutivo de alto nivel para clientes corporativos. "
        f"Usa referencias numéricas [n]. Finaliza con una recomendación de impacto."
    )
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"⚠️ IA ocupada, intente de nuevo."

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/ffffff/checked-user-male.png", width=80) # Placeholder logo
    st.title("Public Go Control")
    alcance = st.radio("Corte Temporal:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.info("Búsqueda optimizada en: Banca y Negocios, Petroguía, Hispanopost y otros 4 medios clave.")

# --- CUERPO PRINCIPAL ---
st.title("🛡️ Strategic Insight Dashboard")
st.write(f"Análisis correspondiente al: **{datetime.now().strftime('%d/%m/%Y')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Gobierno OR "Delcy Rodríguez" OR "Diosdado Cabello" OR "Asamblea Nacional")',
    "🛢️ ENERGÍA": 'Venezuela (Petróleo OR PDVSA OR Petroguia OR Chevron OR Energía OR "Licencia 41")',
    "💰 ECONOMÍA": 'Venezuela (Banca OR "Banca y Negocios" OR Inflación OR Dólar OR "Cámara de Comercio")',
    "🌎 RELACIONES": 'Venezuela (EEUU OR Sanciones OR "HispanoPost" OR Diplomacia OR Trump)'
}
codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}

if 'analisis' not in st.session_state:
    st.session_state['analisis'] = {}

if st.button("🚀 ACTUALIZAR MONITOREO Y MEDIOS"):
    st.session_state['ver_noticias'] = True
    st.session_state['analisis'] = {}

if st.session_state.get('ver_noticias'):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_rss(q, codigos[alcance])
        
        if noticias:
            col_n, col_d = st.columns([1.8, 1.2])
            with col_n:
                st.write("**📌 Noticias Destacadas**")
                for j, n in enumerate(noticias, 1):
                    st.markdown(f"<div class='news-item'><span class='ref-tag'>[{j}]</span><a href='{n['link']}' target='_blank' class='news-link'>{n['titulo'].split(' - ')[0]}</a></div>", unsafe_allow_html=True)
            
            with col_d:
                st.write("**🧠 Intel de Public Go**")
                if st.button(f"🔍 Analizar {cat}", key=f"btn_{cat}"):
                    with st.spinner("Generando..."):
                        res = generar_analisis_categoria(cat, noticias, alcance)
                        st.session_state['analisis'][cat] = res
                
                if cat in st.session_state['analisis']:
                    contenido = st.session_state['analisis'][cat]
                    st.markdown(f"<div class='analysis-box'>{contenido}</div>", unsafe_allow_html=True)
                    
                    url_wa = crear_link_whatsapp(contenido)
                    st.markdown(f"""<a href="{url_wa}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:5px; cursor:pointer; font-weight:bold;">
                        📲 Enviar Reporte a WhatsApp
                        </button></a>""", unsafe_allow_html=True)
        else:
            st.info(f"No hay reportes recientes en {cat}.")

st.divider()
st.caption("Propiedad Intelectual de Public Go Consultores.")
