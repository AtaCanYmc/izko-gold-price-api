from __future__ import annotations

from flask import Flask, Response, jsonify

from .scrape import load_config, scrape

app = Flask(__name__)


@app.route("/izko")
def main_resource():
    cfg = load_config()
    return jsonify(cfg["api"]), 200


@app.route("/izko/bundle", methods=["GET"])
def bundle() -> tuple[Response, int] | Response:
    cfg = load_config()
    content, status = scrape(cfg=cfg)
    return jsonify(content), status


def main() -> None:
    cfg = load_config()
    app.run(
        debug=cfg["api"]["debug"],
        host=cfg["api"]["host"],
        port=cfg["api"]["port"],
    )


if __name__ == "__main__":
    main()
