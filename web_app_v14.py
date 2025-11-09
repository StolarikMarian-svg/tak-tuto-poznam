"""
🎶 Tak túto poznám! – Spotify hra 🇸🇰🇨🇿
Verzia: v14 (Render-ready, stable)

🧾 CHANGELOG:
- ✅ 100 % kompatibilné s Render
- 🚫 Filtruje live/remaster/deluxe verzie
- 🎨 Moderný webový dizajn (tmavé pozadie)
"""

from flask import Flask, render_template_string, redirect
import random
import os
import pathlib
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Cache umiestnenie (v bezpečnom priečinku používateľa) ---
CACHE_PATH = pathlib.Path.home() / ".spotify_cache"
os.makedirs(CACHE_PATH, exist_ok=True)

# --- Spotify údaje ---
CLIENT_ID = "cfeb950f904249629dfd0346d7e6b3e3"
CLIENT_SECRET = "95d3996bc94a4498898118bcc51749b1"
REDIRECT_URI = "https://tak-tuto-poznam.onrender.com/callback"  # Render-friendly callback
SCOPE = "user-read-playback-state,user-modify-playback-state,streaming"

# --- Spotify inicializácia ---
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=str(CACHE_PATH / "token.txt")
))

# --- CZ/SK interpreti ---
ARTISTS = [
    "Elán", "IMT Smile", "Team", "Richard Müller", "No Name", "Kabát",
    "Lucie", "Miro Žbirka", "Chinaski", "Desmod", "Tublatanka",
    "Zuzana Smatanová", "Kryštof", "Mirai", "Peter Nagy",
    "Ewa Farna", "Gladiator", "Tomáš Klus", "Rytmus", "Para",
    "Vidiek", "Olympic", "Karel Gott", "Karel Kryl", "Václav Neckář",
    "Marta Kubišová", "Marika Gombitová", "Karol Duchoň",
    "Pavol Hammel", "Dežo Ursiny", "Jana Kirschner", "Lucie Bílá",
    "Daniel Landa", "Ben Cristovao", "Kali", "Kristína",
    "Peter Lipa", "Hex", "Polemic", "Adam Ďurica",
    "Horkýže Slíže", "Slza", "Sebastian", "Valdemar Matuška",
    "Nedvědovci", "Buty", "Michal Tučný", "Majk Spirit", "Hudba z Marsu"
]

played_songs = set()

# --- Flask aplikácia ---
app = Flask(__name__)

# --- Funkcie ---
def random_cz_sk_song():
    """Vyberie náhodnú CZ/SK pesničku bez opakovania a bez live/remaster."""
    global played_songs
    tries = 0
    while tries < 50:
        artist = random.choice(ARTISTS)
        results = sp.search(q=f"artist:{artist}", type="track", limit=15)
        if results["tracks"]["items"]:
            valid_tracks = []
            for song in results["tracks"]["items"]:
                real_artist = song["artists"][0]["name"].lower().strip()
                title = song["name"].lower()
                album = song["album"]["name"].lower()
                if real_artist != artist.lower().strip():
                    continue
                if any(x in title for x in ["live", "živě", "naživo", "remix"]):
                    continue
                if any(x in album for x in ["live", "živě", "naživo", "remaster", "deluxe", "výběr", "best of"]):
                    continue
                valid_tracks.append(song)
            if valid_tracks:
                song = random.choice(valid_tracks)
                title = song["name"]
                artist_name = song["artists"][0]["name"]
                year = song["album"]["release_date"][:4]
                uri = song["uri"]
                song_id = f"{artist_name} - {title}"
                if song_id not in played_songs:
                    played_songs.add(song_id)
                    return title, artist_name, year, uri
        tries += 1
    return None, None, None, None

# --- Webové rozhranie ---
@app.route("/")
def index():
    title, artist, year, uri = random_cz_sk_song()
    if not uri:
        return "<h2>🎉 Všetky dostupné pesničky už boli prehrané!</h2>"

    html = f"""
    <html>
    <head>
        <title>🎶 Tak túto poznám!</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #0b1a2a;
                color: white;
                text-align: center;
                padding: 40px;
            }}
            h1 {{ color: #00ffcc; }}
            .button {{
                background-color: #00ffcc;
                color: black;
                padding: 15px 30px;
                font-size: 18px;
                border: none;
                border-radius: 8px;
                margin: 10px;
                cursor: pointer;
                text-decoration: none;
            }}
            .button:hover {{
                background-color: #00cca3;
            }}
        </style>
    </head>
    <body>
        <h1>🎵 Tak túto poznám!</h1>
        <p>🎧 Prebieha prehrávanie... hádaj pesničku!</p>
        <p id="info" style="font-size: 22px; margin: 40px;">❓❓❓</p>
        <button class="button" onclick="showInfo()">👀 Zobraziť odpoveď</button>
        <a href="/next" class="button">➡️ Ďalšia pesnička</a>
        <script>
            function showInfo() {{
                document.getElementById("info").innerHTML = "{artist} – {title} ({year})";
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/next")
def next_song():
    return redirect("/")

# --- Render / Lokálny server ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
