import streamlit as st  # <--- ESTA LÍNEA DEBE IR PRIMERO
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import urllib.parse

# Ahora sí puedes usar st.cache_data
@st.cache_data(ttl=600)
def buscar_rss(query, periodo):
    # (Aquí va el resto de la función que actualizamos antes)
    fuentes_lista = [
        "bancaynegocios.com", 
        "petroguia.com", 
        "hispanopost.com", 
        "efectococuyo.com", 
        "elestimulo.com", 
        "finanzasdigital.com"
    ]
    
    sitios_query = " OR ".join([f"site:{s}" for s in fuentes_lista])
    full_query = f"({query}) ({sitios_query})"
    
    params = {
        "q": f"{full_query} when:{periodo}",
        "hl": "es-419",
        "gl": "VE",
        "ceid": "VE:es-419"
    }
    
    url = "https://news.google.com/rss/search"
    results = []
    try:
        r = requests.get(url, params=params, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'xml')
            items = soup.find_all('item')
            
            # Si la búsqueda cerrada falla, intentamos abierta
            if not items:
                params["q"] = f"{query} when:{periodo}"
                r = requests.get(url, params=params, timeout=12)
                soup = BeautifulSoup(r.text, 'xml')
                items = soup.find_all('item')

            for item in items[:8]:
                results.append({
                    "titulo": item.title.get_text(),
                    "link": item.link.get_text()
                })
    except Exception as e:
        st.error(f"Error en conexión: {e}")
    return results

# --- RESTO DEL CÓDIGO (Configuración de IA, Interfaz, etc.) ---
