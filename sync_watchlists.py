import requests
import json

# === CREDENCIALES DE TRAKT ===
CLIENT_ID = "AI5BvFtjiKEFUpOUg3nA8KnCJ5rLhEyt-F79cMqAe2w"
ACCESS_TOKEN = "NavfBOyEmnAlwQrfFflFSFcKRYkilgga"

# === CONFIGURACIÓN DE USUARIOS (USANDO ID NUMÉRICO DIRECTO) ===
USERS_CONFIG = [
    {
        "nombre": "Lucas",
        "render_url": "https://service-web-xfbg.onrender.com/lucaspsara/watchlist/",
        "trakt_list_id": "37858834"
    },
    {
        "nombre": "Ana",
        "render_url": "https://service-web-xfbg.onrender.com/anxhtt/watchlist/",
        "trakt_list_id": "37858835"
    }
]

HEADERS = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": CLIENT_ID,
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def sync_user(config):
    print(f"\n--- Sincronizando lista de {config['nombre']} ---")
    try:
        res = requests.get(config['render_url'], timeout=60)
        items = res.json()
    except Exception as e:
        print(f"Error consultando Render para {config['nombre']}: {e}")
        return

    movies_to_add = []
    for item in items:
        if "tmdb_id" in item and item["tmdb_id"]:
            movies_to_add.append({"ids": {"tmdb": int(item["tmdb_id"])}})
        elif "imdb_id" in item and item["imdb_id"]:
            movies_to_add.append({"ids": {"imdb": item["imdb_id"]}})
        elif "id" in item and str(item["id"]).isdigit():
            movies_to_add.append({"ids": {"tmdb": int(item["id"])}})

    if not movies_to_add:
        print("No se encontraron identificadores válidos en el JSON de Render.")
        return

    # Usamos el endpoint oficial por ID numérico en la cuenta autenticada
    endpoint = f"https://api.trakt.tv/users/me/lists/{config['trakt_list_id']}/items"
    payload = {"movies": movies_to_add}

    post_res = requests.post(endpoint, headers=HEADERS, data=json.dumps(payload))
    if post_res.status_code in [200, 201]:
        resultado = post_res.json()
        agregadas = resultado.get('added', {}).get('movies', 0)
        existentes = resultado.get('existing', {}).get('movies', 0)
        not_found = resultado.get('not_found', {}).get('movies', [])
        print(f"Resultado: {agregadas} agregadas, {existentes} ya estaban en la lista.")
        if not_found:
            print(f"No encontradas en Trakt: {len(not_found)}")
    else:
        print(f"Error en Trakt ({post_res.status_code}): {post_res.text}")

if __name__ == "__main__":
    for user in USERS_CONFIG:
        sync_user(user)