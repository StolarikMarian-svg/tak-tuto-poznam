from flask import Flask, render_template_string
import random
import os
import pathlib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- Cache dir (nemusí veľmi robiť, ale nevadí) ---
CACHE_PATH = pathlib.Path.home() / ".spotify_cache"
os.makedirs(CACHE_PATH, exist_ok=True)

# --- Environment variables ---
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Chýba SPOTIFY_CLIENT_ID alebo SPOTIFY_CLIENT_SECRET v Environment Variables Renderu")

# --- Spotify client credentials ---
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# CZ/SK interpreti
ARTISTS = [
    "Elán",
    "IMT Smile",
    "Kabát",
    "Chinaski",
    "Team",
    "No Name",
    "Richard Müller",
    "Lucie",
    "Inekafe",
]

def random_cz_sk_song():
    artist = random.choice(ARTISTS)
    results = sp.search(q=f"artist:{artist}", type="track", limit=15, market="SK")

    tracks = results.get("tracks", {}).get("items", [])
    if not tracks:
        # keď náhodou nič nenájde, skúsi iného interpreta
        return random_cz_sk_song()

    track = random.choice(tracks)

    title = track["name"]
    artist_name = ", ".join(a["name"] for a in track["artists"])
    year = track["album"]["release_date"].split("-")[0]
    uri = track["uri"]
    uri_id = uri.split(":")[-1]

    return title, artist_name, year, uri_id


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
      background: rgba(0, 0, 0, 0.9);
      border-radius: 24px;
      padding: 32px 28px;
      max-width: 480px;
      width: 100%;
      box-shadow: 0 18px 45px rgba(0, 0, 0, 0.9);
      text-align: center;
    }
    h1 {
      font-size: 2rem;
      margin-bottom: 0.5rem;
    }
    .subtitle {
      opacity: 0.8;
      font-size: 0.95rem;
      margin-bottom: 1.8rem;
    }
    .song {
      font-size: 1.3rem;
      margin-bottom: 0.5rem;
    }
    .meta {
      opacity: 0.8;
      margin-bottom: 1.5rem;
    }
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
      margin-top: 0.6rem;
    }
    .btn:hover {
      opacity: 0.92;
      transform: translateY(-1px);
    }
    .icon-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.4);
      background: transparent;
      color: #fff;
      cursor: pointer;
      margin-left: 0.5rem;
      font-size: 1.2rem;
    }
    .icon-btn:hover {
      background: rgba(255,255,255,0.05);
    }
    #solution {
      display: none;
      margin-top: 1rem;
    }
    #placeholder {
      margin-bottom: 0.8rem;
    }
    .hint {
      margin-top: 1.2rem;
      font-size: 0.8rem;
      opacity: 0.75;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>🎶 Tak túto poznám!</h1>
    <div class="subtitle">
      Uhádni pesničku – CZ/SK edícia
    </div>

    <!-- najprv len otázniky -->
    <div id="placeholder">
      <div class="song">???? – ????</div>
      <div class="meta">(rok skrytý)</div>
    </div>

    <!-- skutočné riešenie (skryté) -->
    <div id="solution">
      <div class="song">{{ title }} – {{ artist }}</div>
      <div class="meta">({{ year }})</div>
    </div>

    <div>
      <a class="btn" href="https://open.spotify.com/track/{{ uri_id }}" target="_blank" rel="noopener">
        ▶️ Pustiť na Spotify
      </a>
      <button id="revealBtn" class="icon-btn" title="Ukáž riešenie" aria-label="Ukáž riešenie">
        👁
      </button>
    </div>

    <div class="hint">
      Pesničku si pusti na Spotify a skús ju uhádnuť. <br>
      Klikni na 👁, keď chceš vidieť správnu odpoveď.
      <br>Refreshni stránku pre ďalšiu pesničku.
    </div>
  </div>

  <script>
    const revealBtn = document.getElementById('revealBtn');
    const solution = document.getElementById('solution');
    const placeholder = document.getElementById('placeholder');

    revealBtn.addEventListener('click', () => {
      solution.style.display = 'block';
      placeholder.style.display = 'none';
      revealBtn.style.display = 'none';
    });
  </script>
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
        uri_id=uri_id,
    )
