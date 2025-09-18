# app.py
import json
from flask import Flask, jsonify, Response

from scrape import scrape

with open("config.json", "r") as f:
    config = json.load(f)
app = Flask(__name__)

@app.route("/izko")
def main_resource():
    return jsonify(config["api"]), 200

@app.route("/izko/bundle", methods=["GET"])
def bundle() -> tuple[Response, int] | Response:
    content, status = scrape()
    return jsonify(content), status


if __name__ == "__main__":
    app.run(
        debug=config["api"]["debug"],
        host=config["api"]["host"],
        port=config["api"]["port"]
    )
