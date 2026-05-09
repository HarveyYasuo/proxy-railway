# Roblox Server Proxy - Railway Deployment Guide

## 1. Backend Setup (Railway)

### 1.1 Create folder structure
```
proxy/
├── main.py
├── requirements.txt
└── Procfile
```

### 1.2 Push to GitHub
```bash
cd proxy
git init
git add .
git commit -m "Initial proxy server"
git branch -M main
git remote add origin https://github.com/TU_USER/proxy-railway.git
git push -u origin main
```

### 1.3 Deploy on Railway
1. Go to https://railway.app
2. Login with GitHub
3. New Project → Deploy from GitHub repo
4. Select your `proxy-railway` repo
5. Railway auto-detects FastAPI and deploys
6. Copy your URL: `https://proxy-xxx.up.railway.app`

---

## 2. Client Update (Local app.py)

Replace `obtener_todos_servidores()` with:

```python
def obtener_todos_servidores(place_id, session):
    proxy_url = "https://proxy-xxx.up.railway.app"
    try:
        r = requests.get(f"{proxy_url}/servers/{place_id}", timeout=30)
        data = r.json()
        return data.get("servers", [])
    except Exception:
        return []
```

---

## 3. Latency Test

Test proxy ping vs real ping:
```bash
# Ping from your laptop to AWS Virginia
ping dynamodb.us-east-1.amazonaws.com

# Expected: ~86ms (your real latency to US-East)
```

---

## 4. Expected Flow

```
Your Laptop (Colombia)
       │
       │  GET /servers/123456
       ▼
   Railway Proxy (US-East, Virginia)
       │
       │  Roblox sees requests from Virginia IP
       ▼
   Roblox API returns servers
       │
       │  Filter: fps>=57, ping 70-110ms
       ▼
   Return top 5 best servers
       │
       │  Client displays clean list
       ▼
   User clicks UNIRSE → Roblox Player launches
```

---

## 5. API Reference

### GET /servers/{place_id}
```
Parameters:
- min_fps: int (default 57)
- min_ping: int (default 70)
- max_ping: int (default 110)

Response:
{
  "servers": [
    {
      "id": "uuid...",
      "playing": 45,
      "maxPlayers": 50,
      "fps": 60,
      "ping": 75,
      "available": 5
    }
  ],
  "total": 100,
  "filtered": 12
}
```