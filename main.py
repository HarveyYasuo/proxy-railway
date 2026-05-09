from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI(title="Roblox Server Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROBLOX_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.roblox.com/",
    "Origin": "https://www.roblox.com",
}

MIN_FPS = 57
MIN_PING = 70
MAX_PING = 110


@app.get("/")
def home():
    return {"status": "ok", "service": "Roblox Server Proxy"}


@app.get("/servers/{place_id}")
def get_servers(
    place_id: int,
    min_fps: int = Query(default=MIN_FPS, ge=0, le=60),
    min_ping: int = Query(default=MIN_PING, ge=0),
    max_ping: int = Query(default=MAX_PING, ge=0)
):
    """
    Obtiene servidores filtrados de Roblox.
    Filtra por FPS y ping para priorizar servidores US-East.
    """
    servers = fetch_servers(place_id)
    
    if not servers:
        return {"servers": [], "total": 0, "filtered": 0}
    
    filtered = []
    for srv in servers:
        fps = srv.get("fps", 60)
        ping = srv.get("ping", 999)
        playing = srv.get("playing", 0)
        max_players = srv.get("maxPlayers", 1)
        
        if fps < min_fps:
            continue
        if ping < min_ping or ping > max_ping:
            continue
        
        filtered.append({
            "id": srv["id"],
            "playing": playing,
            "maxPlayers": max_players,
            "fps": fps,
            "ping": ping,
            "available": max_players - playing,
        })
    
    filtered.sort(key=lambda x: (-x["fps"], -x["available"]))
    top5 = filtered[:5]
    
    return {
        "servers": top5,
        "total": len(servers),
        "filtered": len(filtered),
    }


def fetch_servers(place_id: int, max_results: int = 200):
    """Descarga servidores de Roblox con paginación."""
    servers = []
    cursor = ""
    
    while len(servers) < max_results:
        url = f"https://games.roblox.com/v1/games/{place_id}/servers/Public"
        params = {
            "sortOrder": "Asc",
            "limit": 100,
            "excludeFullGames": "false"
        }
        if cursor:
            params["cursor"] = cursor
        
        try:
            r = requests.get(url, headers=ROBLOX_HEADERS, params=params, timeout=15)
            data = r.json()
        except Exception:
            break
        
        page = data.get("data", [])
        if not page:
            break
        
        servers.extend(page)
        cursor = data.get("nextPageCursor", "")
        if not cursor:
            break
    
    return servers
