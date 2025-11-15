from flask import Flask, render_template_string
import random
import os
import pathlib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- Cache dir (bez OAuth to nič nerobí, ale môže ostať) ---
CACHE_PATH = pathlib.Path.home() / ".spotify_cache"
os.makedirs(CACHE_PATH, exist_ok=True)

# --- Environment variables ---
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")  # berie tvoju env premennú

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Chýba SPOTIFY_CLIENT_ID alebo CLIENT_SECRET v Environment Variables Renderu")

# --- Spotify client credentials ---
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# CZ/SK interpreti
ARTISTS = [
    "Elán", "IMT Smile", "Kabát", "Chinaski",
    "Team", "No Name", "Richard Müller", "Lucie", "Inekafe"
]

def random_cz_sk_song():
    artist = random.choice(ARTISTS)
    results = sp.search(q=f"artist:{artist}", type="track", limit=15, market="SK")

    tracks = results.get("tracks", {}).get("items", [])
    if not tracks:
        return random_cz_sk_song()

    track = random.choice(tracks)

    title = track["name"]
    artist_name = ", ".join(a["name"] for a in track["artists"])
    year = track["album"]["release_date"].split("-")[0]
    uri_id = track["uri"].split(":")[-1]

    return title, artist_name, year, uri_id


# --- Flask ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="sk">
<head>
  <meta charset="utf-8">
  <title>Tak túto poznám! 🎶</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(circle at top, #1db954 0, #121212 40%, #000 100%);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .card {
      background: rgba(0, 0, 0, 0.75);
      border-radius: 24px;
      padding: 32px 28px;
      max-width: 420px;
      width: 100%;
      box-shadow: 0 18px 45px rgba(0, 0, 0, 0.9);
      text-align: center;
    }
    h1 { font-size: 1.7rem; margin-bottom: 0.5rem; }
    .subtitle { opacity: 0.8; font-size: 0.95rem; margin-bottom: 2rem; }
    .song { font-size: 1.3rem; margin-bottom: 0.5rem; }
    .meta { opacity: 0.8; margin-bottom: 1.5rem; }
    .btn {
      display: inline-block;
      padding: 0.7rem 1.4rem;
      border-radius: 999px;
      border: none;
      font-size: 1rem;
      cursor: pointer;
      background: #1db954;
      color: #000;
      text-decoration: none;
    }
    .btn:hover { opacity: 0.92; transform: translateY(-1px); }
  </style>
</head>
<body>
  <div class="card">
    <h1>🎶 Tak túto poznám!</h1>
    <div class="subtitle">Uhádni pesničku – CZ/SK edícia</div>

    <div class="song">{{ title }} – {{ artist }}</div>
    <div class="meta">({{ year }})</div>

    <a class="btn" href="https://open.spotify.com/track/{{ uri_id }}" target="_blank">▶️ Pustiť na Spotify</a>

    <p style="margin-top: 1.5rem; font-size: .8rem; opacity: .7;">
      Refreshni stránku pre ďalšiu pesničku.
    </p>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    title, artist, year, uri_id = random_cz_sk_song()
    return render_template_string(
        HTML_TEMPLATE,
        title=title,
        artist=artist,
        year=year,
        uri_id=uri_id
    )

