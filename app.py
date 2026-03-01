# --- PROCESAMIENTO ULTRA-ROBUSTO ---
        texto_full = str(row.get("Analisis", "")).replace("SEPARADOR", "").strip()
        
        # Normalizamos el texto para la búsqueda (todo a mayúsculas y sin espacios raros)
        texto_upper = texto_full.upper()
        
        # Lista de posibles llaves que la IA podría escribir
        keywords = ["RECOMENDACIÓN EJECUTIVA", "RECOMENDACIÓN", "RECOMENDACION"]
        cuerpo = texto_full
        rec_texto = ""

        for word in keywords:
            if word in texto_upper:
                # Encontramos la posición exacta de la palabra clave
                pos = texto_upper.find(word)
                # El cuerpo es todo lo que está antes
                cuerpo = texto_full[:pos].strip()
                # La recomendación es todo lo que está después (saltando la palabra clave y posibles ":" o " ")
                resto = texto_full[pos + len(word):].strip()
                rec_texto = resto.lstrip(":").strip()
                break

        # Limpieza final de títulos que Gemini a veces repite
        cuerpo_limpio = cuerpo.replace("Perspectiva Estratégica:", "").replace("Análisis del Impacto:", "").strip()

        with st.container():
            st.markdown(f'<div class="report-card">', unsafe_allow_html=True)
            col_info, col_anid = st.columns([1, 2])
            
            with col_info:
                st.markdown(f'<span class="cat-tag" style="background-color: {bg_color}; color: white;">{cat_limpia}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="noticia-titulo">{row["Noticia"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<a href="{row["Link"]}" target="_blank" class="fuente-link">🔗 Leer fuente original</a>', unsafe_allow_html=True)
                st.caption(f"📅 Corte Informativo")

            with col_anid:
                st.markdown("##### 🧠 Perspectiva Estratégica")
                st.markdown(f'<div class="analisis-box">{cuerpo_limpio}</div>', unsafe_allow_html=True)
                
                # Si rec_texto tiene contenido real, mostramos la caja azul
                if len(rec_texto) > 5: 
                    st.info(f"**💡 RECOMENDACIÓN PARA LA ALTA GERENCIA:**\n\n{rec_texto}")
                else:
                    st.warning("⚠️ Análisis en proceso de síntesis estratégica.")
            
            st.markdown('</div>', unsafe_allow_html=True)
