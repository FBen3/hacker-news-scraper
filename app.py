from flask import Flask, request, jsonify

from src.scraper.scraper import parse_pages
from src.scraper.mongo_db import save_scraped_data, fetch_saved_articles


app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"message": "This is Ben's Hacker News custom scraper API!"})


if __name__ == "__main__":
    app.run(debug=True)



