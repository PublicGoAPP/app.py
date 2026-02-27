import streamlit as st
import google.generativeai as genai
import time

# Limpiamos cualquier configuración previa
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Forzamos un modelo más ligero para la prueba
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error de configuración: {e}")

st.title("🛡️ Public Go: Test de Conexión")

if st.button("🚀 PROBAR CONEXIÓN DE INTELIGENCIA"):
    try:
        with st.spinner("Estableciendo puente con Google..."):
            # Una petición ultra simple para ver si el canal está abierto
            response = model.generate_content("Responde solo: 'Conexión Exitosa'")
            st.success(f"✅ {response.text}")
            st.balloons()
    except Exception as e:
        st.error("❌ El canal de comunicación sigue cerrado.")
        st.info("Sugerencia: Intenta cambiar de conexión (WiFi a Datos Móviles) o verifica si hay espacios vacíos en tus Secrets.")
        st.write(f"Detalle técnico del error: {e}")
