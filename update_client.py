"""
Actualización para app.py - Integrar con Proxy Railway

Instructions:
1. Reemplaza las funciones de obtener_todos_servidores en app.py
2. Actualiza la URL del proxy con tu URL de Railway
"""

# ===================== REEMPLAZAR EN app.py =====================

# Función REEMPLAZADA en app.py:
def obtener_todos_servidores(place_id, session):
    """
    Descarga servidores via Proxy Railway (US-East).
    El proxy filtra servidores con fps>=57 y ping 70-110ms.
    """
    PROXY_URL = "https://TU-PROXY-xxx.up.railway.app"  # ← Cambiar por tu URL

    try:
        r = requests.get(f"{PROXY_URL}/servers/{place_id}", timeout=30)
        data = r.json()
        return data.get("servers", [])
    except Exception as e:
        print(f"[ERROR] Proxy no disponible: {e}")
        # Fallback: consulta directa
        return _fetch_direct_servers(place_id)


def _fetch_direct_servers(place_id):
    """Fallback si el proxy falla."""
    resultado, cursor, consultados = [], "", 0
    while consultados < 200:
        url = (
            f"https://games.roblox.com/v1/games/{place_id}/servers/Public"
            f"?sortOrder=Asc&limit=100&excludeFullGames=false"
            + (f"&cursor={cursor}" if cursor else "")
        )
        try:
            r = requests.get(url, timeout=15)
            data = r.json()
        except Exception:
            break
        pagina = data.get("data", [])
        if not pagina:
            break
        resultado.extend(pagina)
        consultados += len(pagina)
        cursor = data.get("nextPageCursor", "")
        if not cursor:
            break
    return resultado

# ============================================================

# Para aplicar manualmente:
# 1. Abre app.py
# 2. Busca la función obtener_todos_servidores
# 3. Reemplaza TODO su contenido con el código de arriba
# 4. Cambia PROXY_URL por tu URL de Railway