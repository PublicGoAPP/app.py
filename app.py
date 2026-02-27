import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# --- 1. CONEXIÓN IA ---
def conectar_ia():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

model = conectar_ia()

st.set_page_config(page_title="Public Go Elite", layout="wide")

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; text-transform: uppercase; border-left: 8px solid #f1c40f; }
    .news-item { border-bottom: 1px solid #eee; padding: 10px 0; }
    .news-link { color: #003b5c; text-decoration: none; font-weight: bold; font-size: 1rem; }
    .risk-box { border-left: 5px solid #003b5c; background-color: #f0f7f9; padding: 15px; border-radius: 5px; margin-top: 10px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE BÚSQUEDA (Reforzado para no dar "Vacío") ---
def buscar_noticias(query, periodo):
    codigos = {"Hoy": "1d", "Semana": "7d", "Mes": "30d"}
    p = codigos.get(periodo, "7d") # Si falla el periodo, busca la semana por defecto
    
    # Query simplificada para asegurar resultados
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:{p}&hl=es-419&gl=VE&ceid=VE:es-419"
    
    results = []
    try:
        r = requests.get(url, timeout=15)
        soup = BeautifulSoup(r.text, 'xml')
        items = soup.find_all('item')
        
        # Si no hay noticias hoy, forzamos búsqueda de la semana automáticamente
        if not items and periodo == "Hoy":
            url_backup = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:7d&hl=es-419&gl=VE&ceid=VE:es-419"
            r = requests.get(url_backup, timeout=15)
            soup = BeautifulSoup(r.text, 'xml')
            items = soup.find_all('item')

        for item in items[:6]:
            results.append({"titulo": item.title.get_text().split(" - ")[0], "link": item.link.get_text()})
    except:
        pass
    return results

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Public Go")
    alcance = st.radio("Filtro Temporal:", ["Hoy", "Semana", "Mes"], index=1) # Por defecto en Semana para que no salga vacío
    st.divider()
    st.metric("Tasa BCV", "417.35 Bs", "+0.79%")
    st.metric("EMBI", "18,450 bps", "-50 bps")

# --- 5. CUERPO PRINCIPAL ---
st.title("🛡️ Public Go: AI Strategic Hub")

CATEGORIAS = {
    "🏛️ GOBIERNO": "Venezuela politica",
    "🛢️ ENERGÍA": "Venezuela petroleo PDVSA",
    "💰 ECONOMÍA": "Venezuela economia",
    "🌎 RELACIONES": "Venezuela sanciones"
}

for cat, q in CATEGORIAS.items():
    st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
    noticias = buscar_noticias(q, alcance)
    
    if noticias:
        col1, col2 = st.columns([1.6, 1.4])
        with col1:
            st.write("**📌 Eventos**")
            texto_ia = ""
            for n in noticias:
                st.markdown(f"<div class='news-item'><a href='{n['link']}' target='_blank' class='news-link'>{n['titulo']}</a></div>", unsafe_allow_html=True)
                texto_ia += f"- {n['titulo']}\n"
        with col2:
            st.write("**🧠 Riesgo**")
            if st.button(f"Analizar {cat}", key=f"btn_{cat}"):
                if model:
                    with st.spinner("IA analizando..."):
                        res = model.generate_content(f"Analiza el riesgo de: {texto_ia}")
                        st.markdown(f"<div class='risk-box'>{res.text}</div>", unsafe_allow_html=True)
                else:
                    st.warning("IA no conectada.")
    else:
        st.info(f"Sin noticias detectadas en {cat} para este filtro.")

st.caption(f"Corte: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
