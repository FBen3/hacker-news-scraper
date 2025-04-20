from datetime import datetime
from flask import Flask, request, jsonify

from src.scraper.config import WEBSITES
from src.scraper.scraper import parse_pages
from src.scraper.mongo_db import (
    save_scraped_data, 
    fetch_saved_articles,
    fetch_keywords,
    update_keywords
)


app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"message": "This is Ben's HackerNews custom scraper!"})


@app.route("/api/scrape", methods=["POST"])
def scrape_now():
    data = parse_pages(WEBSITES)
    save_scraped_data(data)


@app.route("/api/articles", methods=["GET"])
def get_saved_articles():
    date_str = request.args.get("date")  # e.g. /api/articles?date=2025-02-18


    articles = fetch_saved_articles()
    return jsonify({"message": f"Currently saved articles: {articles}"})




@app.route("/api/keywords", methods=["GET"])
def get_keywords():
    keyword_list = fetch_keywords()
    return jsonify({"message": f"Current keywords: {keyword_list}"})


@app.route("api/update_keywords", methods=["POST"])
def update_keyword(keywords=None):
    result = update_keywords(keywords)
    return jsonify({"message": result})


if __name__ == "__main__":
    app.run(debug=True)



