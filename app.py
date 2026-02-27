import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURACIÓN SEGURA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error: Configure su API Key en los Secrets de Streamlit.")

st.set_page_config(page_title="Public Go OSINT", layout="wide")

# --- DISEÑO ELITE ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #003b5c !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .cat-header { background-color: #003b5c; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 20px; }
    .analysis-box { background-color: #f0f7f9; padding: 15px; border-left: 6px solid #003b5c; margin-bottom: 20px; border-radius: 0 0 8px 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE BÚSQUEDA POR INTERVALO ---
def buscar_osint(query, f_inicio, f_fin):
    # Formateamos las fechas para Google: MM/DD/YYYY
    d1 = f_inicio.strftime('%m/%d/%Y')
    d2 = f_fin.strftime('%m/%d/%Y')
    
    # El secreto: tbs=cdr:1,cd_min:...,cd_max:...
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=nws&tbs=cdr:1,cd_min:{d1},cd_max:{d2}"
    
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Buscamos los contenedores de noticias de Google
        for g in soup.find_all('div', class_='So007e')[:8]:
            link = g.find('a')['href']
            title = g.find('div', role='heading').get_text()
            results.append({"titulo": title, "link": link})
    except: pass
    return results

# --- INTERFAZ ---
with st.sidebar:
    st.markdown("### 📅 Filtro Temporal OSINT")
    tipo_busqueda = st.radio("Método de búsqueda:", ["Rangos Predefinidos", "Intervalo Personalizado"])
    
    if tipo_busqueda == "Intervalo Personalizado":
        fecha_inicio = st.date_input("Desde:", datetime(2026, 2, 1))
        fecha_fin = st.date_input("Hasta:", datetime.now())
    else:
        alcance = st.radio("Alcance:", ["Hoy", "Semana"])
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=1 if alcance == "Hoy" else 7)

    st.divider()
    st.metric("PIB 2026 (Est.)", "10%", "+2.5%")

st.markdown("<h1 style='color: #003b5c;'>🛡️ Public Go: OSINT Intelligence</h1>", unsafe_allow_html=True)
st.write(f"Analizando desde el **{fecha_inicio.strftime('%d/%b')}** hasta el **{fecha_fin.strftime('%d/%b')}**")

CATEGORIAS = {
    "🏛️ GOBIERNO": 'Venezuela (Fiscal OR "Larry Devoe" OR "Saab" OR "Amnistia")',
    "🛢️ ENERGÍA": 'Venezuela (Shell OR Chevron OR "PDVSA" OR "gas" OR "crudo")',
    "💰 ECONOMÍA": 'Venezuela (PIB OR "BCV" OR "dolar" OR "inversion")',
    "🇺🇸 RELACIONES": 'Venezuela (Trump OR "Casa Blanca" OR "Sanciones")'
}

if st.button("🚀 INICIAR ESCANEO PROFUNDO"):
    for cat, q in CATEGORIAS.items():
        st.markdown(f"<div class='cat-header'>{cat}</div>", unsafe_allow_html=True)
        noticias = buscar_osint(q, fecha_inicio, fecha_fin)
        
        if noticias:
            titulares = " | ".join([n['titulo'] for n in noticias])
            # La IA ahora sabe exactamente qué fechas está analizando
            prompt = f"Analiza estos eventos de {cat} ocurridos entre el {fecha_inicio} y el {fecha_fin} en Venezuela. Da 3 conclusiones estratégicas."
            try:
                analisis = model.generate_content(prompt).text
                st.markdown(f"<div class='analysis-box'>{analisis}</div>", unsafe_allow_html=True)
            except: st.info("Análisis en proceso...")

            for n in noticias:
                st.markdown(f"📌 **{n['titulo']}** ([Fuente]({n['link']}))")
        else:
            st.markdown("<div class='analysis-box'>No se hallaron registros en este intervalo.</div>", unsafe_allow_html=True)
