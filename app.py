import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# --- 1. CONEXIÓN IA (Independizada) ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Conexión directa para evitar errores 404 en cuentas Pro
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

model = conectar_ia()

st.set_page_config(page_title="Public Go Elite", layout="wide")

# --- 2. ESTILOS CORPORATIVOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; text-transform: uppercase; border-left: 8px solid #f1c40f; }
    .news-item { border-bottom: 1px solid #eee; padding: 10px 0; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: bold; font-size: 1rem; }
    .risk-box { border-left: 5px solid #003b5c; background-color: #f0f7f9; padding: 15px; border-radius: 5px; margin-top: 10px; color: #333; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE BÚSQUEDA (Sin bloqueos) ---
def buscar_noticias(query, periodo):
    codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}
    p = codigos.get(periodo, "1d")
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{p}&hl=es-419&gl=VE&ceid=VE:es-419"
    results = []
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'xml')
        for item in soup.find_all('item')[:6]:
            results.append({"titulo": item.title.get_text().split(" - ")[0], "link": item.link.get_text()})
    except:
        pass
    return results

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Ventana de Análisis:", ["Hoy", "Semana", "Mes"])
    st.divider()
    st.metric("Tasa BCV", "417.35 Bs", "+0.79%")
    st.metric("EMBI (Riesgo País)", "18,450 bps", "-50 bps", delta_color="inverse")

# --- 5. CATEGORÍAS PROFESIONALES (Ampliadas) ---
st.title("🛡️ Strategic Insight Dashboard")
st.write(f"Corte: **{datetime.now().strftime('%d/%m/%Y %H:%M')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO & INSTITUCIONES": "Venezuela política gobierno",
    "🛢️ ENERGÍA & LICENCIAS": "Venezuela petróleo gas PDVSA licencias",
    "💰 ECONOMÍA & FINANZAS": "Venezuela economía inversión dólares",
    "🌎 RELACIONES EXTERNAS": "Venezuela geopolítica diplomacia"
}

# --- 6. GENERACIÓN DE INTERFAZ ---
for cat, query in CATEGORIAS.items():
    st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
    noticias = buscar_noticias(query, alcance)
    
    if noticias:
        col_news, col_ai = st.columns([1.6, 1.4])
        
        with col_news:
            st.write("**📌 Eventos Detectados**")
            titulares_para_ia = ""
            for n in noticias:
                st.markdown(f"<div class='news-item'><a href='{n['link']}' target='_blank' class='news-link'>{n['titulo']}</a></div>", unsafe_allow_html=True)
                titulares_para_ia += f"- {n['titulo']}\n"
        
        with col_ai:
            st.write("**🧠 Inteligencia de Riesgo**")
            # El botón ahora es único para cada categoría para no colapsar la IA
            if st.button(f"Analizar Impacto: {cat.split()[1]}", key=f"btn_{cat}"):
                if model:
                    with st.spinner("Analizando..."):
                        try:
                            prompt = f"Como Directora de Riesgo, analiza brevemente el impacto de estas noticias en el clima de negocios: {titulares_para_ia}"
                            res = model.generate_content(prompt)
                            st.markdown(f"<div class='risk-box'>{res.text}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error de conexión: {e}")
                else:
                    st.warning("IA no conectada. Revisa los Secrets.")
    else:
        st.info(f"Sin eventos críticos detectados para {cat} en este momento.")

st.divider()
st.caption("Uso exclusivo Public Go Consultores. Datos procesados vía OSINT.")
