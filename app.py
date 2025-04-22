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
    # TODO: modify this function, and parse_pages to accept a 
    # number which defines how many pages of HN to scrape.
    data = parse_pages(WEBSITES)
    save_scraped_data(data)
    return jsonify({"status": "success", "data_inserted": data})


@app.route("/api/articles", methods=["GET"])
def get_saved_articles():
    date_str = request.args.get("date")  # e.g. /api/articles?date=2025-02-18
    datetime_arg = None

    if date_str:
        try:
            datetime_arg = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "error": (
                    "Incorrect date format. Please provide a date "
                    "in the form: YYYY-MM-DD"
                )
            })
        except Exception as e:
            raise e

    articles = fetch_saved_articles(date=datetime_arg)
    return jsonify({"message": f"Currently saved articles: {articles}"})


@app.route("/api/keywords", methods=["GET"])
def get_keywords():
    keyword_list = fetch_keywords()
    return jsonify({"message": f"Current keywords: {keyword_list}"})


@app.route("/api/update_keywords", methods=["POST"])
def update_keyword(keywords=None):
    result = update_keywords(keywords)
    return jsonify({"message": result})


if __name__ == "__main__":
    app.run(debug=True)



