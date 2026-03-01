@st.cache_data(ttl=600)
def buscar_rss(query, periodo):
    # 1. Definimos las fuentes prioritarias para Public Go
    fuentes_lista = [
        "bancaynegocios.com", 
        "petroguia.com", 
        "hispanopost.com", 
        "efectococuyo.com", 
        "elestimulo.com", 
        "finanzasdigital.com"
    ]
    
    # 2. Creamos el string de sitios: (site:medio1.com OR site:medio2.com)
    sitios_query = " OR ".join([f"site:{s}" for s in fuentes_lista])
    
    # 3. Construimos el query final:
    # Intentamos primero en los medios clave, si no, Google News ampliará la búsqueda
    full_query = f"({query}) ({sitios_query})"
    
    # 4. URL de Google News (HL y GL configurados para Venezuela)
    params = {
        "q": f"{full_query} when:{periodo}",
        "hl": "es-419",
        "gl": "VE",
        "ceid": "VE:es-419"
    }
    
    # Usamos requests.params para que la codificación sea perfecta
    url = "https://news.google.com/rss/search"
    
    results = []
    try:
        r = requests.get(url, params=params, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'xml')
            items = soup.find_all('item')
            
            # Si no hay resultados con los medios específicos, buscamos en general
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
