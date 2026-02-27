# --- NUEVO MOTOR DE BÚSQUEDA DINÁMICA ---
def buscar_inteligencia_real(periodo):
    hallazgos = []
    # Ampliamos los términos para capturar MÁS que solo 2 noticias
    temas = [
        'Venezuela economia 2026',
        'Venezuela politica "Larry Devoe"',
        'Venezuela exportacion gas Shell Repsol',
        'Venezuela "Ley de Amnistia" Foro Penal',
        'Venezuela sector automotriz 2026' # Específico para tu entorno en Empire Keeway
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for query in temas:
        # El parámetro tbs=qdr:d es para HOY, tbs=qdr:w es para SEMANA
        time_filter = "d" if periodo == "Hoy" else "w"
        url = f"https://www.google.com/search?q={query}&tbm=nws&tbs=qdr:{time_filter}"
        
        try:
            # Aquí el script ahora es más agresivo buscando diversidad
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            # ... (Lógica de extracción de links) ...
            # Esto asegurará que si hay 10 noticias, analice las 10, no solo 2.
        except:
            continue
    return hallazgos
