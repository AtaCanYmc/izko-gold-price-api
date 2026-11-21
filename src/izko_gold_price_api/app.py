from __future__ import annotations

from flask import Flask, Response, jsonify

from .scrape import config, scrape

app = Flask(__name__)


@app.route("/izko")
def main_resource():
    return jsonify(config["api"]), 200


@app.route("/izko/bundle", methods=["GET"])
def bundle() -> tuple[Response, int] | Response:
    content, status = scrape()
    return jsonify(content), status


def main() -> None:
    app.run(
        debug=config["api"]["debug"],
        host=config["api"]["host"],
        port=config["api"]["port"],
    )


if __name__ == "__main__":
    main()
