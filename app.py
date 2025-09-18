# app.py
import json
from flask import Flask, jsonify, Response

with open("config.json", "r") as f:
    config = json.load(f)
app = Flask(__name__)

@app.route("/bundle", methods=["GET"])
def scrape() -> tuple[Response, int] | Response:

    return jsonify({
        "url": url,
        "title": title
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
