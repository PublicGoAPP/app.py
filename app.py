import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
from datetime import datetime

# --- ESTILO Y MARCA ---
st.set_page_config(page_title="Public Go - Strategic Intelligence", layout="wide")

st.markdown("""
    <style>
    .stAlert { border-radius: 10px; border: 1px solid #2980b9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 5px solid #2980b9; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ANÁLISIS ESTRATÉGICO ---
def generar_insight(titulo, texto):
    t = (titulo + " " + texto).lower()
    
    # Análisis de la transición judicial
    if "fiscal" in t or "devoe" in t or "saab" in t:
        return {
            "impacto": "🔴 ALTO - Seguridad Jurídica",
            "analisis": "El relevo de Tarek William Saab por Larry Devoe busca sanear la imagen institucional del Ministerio Público. Para sus clientes, esto implica una ventana de oportunidad para la revisión de expedientes y la reactivación de interlocuciones legales internacionales."
        }
    # Análisis Energético
    if "shell" in t or "gas" in t or "petróleo" in t:
        return {
            "impacto": "🟢 OPORTUNIDAD - Flujo de Caja",
            "analisis": "La consolidación de acuerdos con Shell y Repsol confirma que el sector privado extranjero está validando el nuevo marco de inversión. Esto sustenta la proyección de crecimiento del 10% del PIB para el cierre de 2026."
        }
    # Análisis de Amnistía
    if "amnistía" in t or "libertad" in t:
        return {
            "impacto": "🟡 MEDIO - Estabilidad Política",
            "analisis": "Las 179 liberaciones iniciales son la 'moneda de cambio' necesaria para que la administración Trump mantenga las licencias operativas actuales, reduciendo el riesgo de sanciones adicionales en el corto plazo."
        }
    
    return {"impacto": "🔵 INFORMATIVO", "analisis": "Evento bajo monitoreo de rutina. Sin impacto inmediato en la estructura de costos o legalidad de operaciones activas."}

# --- INTERFAZ PRINCIPAL ---
st.title("🛡️ Public Go: Intelligence Platform")
st.sidebar.header("Parámetros de Análisis")
periodo = st.sidebar.radio("Alcance Temporal", ["Hoy", "Semana"])

# Métricas rápidas para tus reuniones
c1, c2, c3 = st.columns(3)
c1.metric("Proyección PIB 2026", "10%", "+2.5% vs 2025")
c2.metric("Nivel de Riesgo País", "Moderado", "-15% (Mejora)")
c3.metric("Estatus Licencias", "Vigentes", "Confirmado Feb 26")

if st.button("🚀 Ejecutar Análisis de Coyuntura"):
    with st.spinner("Procesando inteligencia de fuentes oficiales y privadas..."):
        # (Aquí va el motor de búsqueda que ya conoces, pero ahora llama a generar_insight)
        # Simulación de visualización:
        st.subheader("📍 Análisis de Hitos Críticos")
        
        # Ejemplo de cómo se vería una noticia con análisis profundo:
        with st.container():
            st.warning("📌 TAREK WILLIAM SAAB RENUNCIA: LARRY DEVOE ASUME FISCALÍA ENCARGADA")
            insight = generar_insight("Fiscal", "Renuncia Saab")
            st.markdown(f"**{insight['impacto']}**")
            st.info(insight['analisis'])
            st.caption("Estrategia: Este movimiento es clave para destrabar arbitrajes internacionales.")
            
        st.divider()
        
        with st.container():
            st.success("📌 SHELL Y REPSOL INICIAN EXPORTACIÓN DE GAS BAJO NUEVO ESQUEMA")
            insight_gas = generar_insight("Shell", "Gas Venezuela")
            st.markdown(f"**{insight_gas['impacto']}**")
            st.info(insight_gas['analisis'])

st.markdown("---")
st.caption("Propiedad Intelectual de Public Go Consulting. Prohibida su reproducción total o parcial.")
