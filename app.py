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
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Chýba SPOTIFY_CLIENT_ID alebo SPOTIFY_CLIENT_SECRET v Environment Variables Renderu")

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
