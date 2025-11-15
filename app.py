from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def index():
    return "OK – minimal Flask app beží 🚀"
