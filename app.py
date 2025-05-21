import logging
from datetime import datetime, date

from flask import Flask, request, jsonify
from flask.json.provider import DefaultJSONProvider

from src.scraper.config import WEBSITES
from src.scraper.scraper import parse_pages
from src.scraper.mongo_db import (
    save_scraped_data, 
    fetch_saved_articles,
    fetch_keywords,
    update_keywords
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)


app = Flask(__name__)

class ISOJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

app.json = ISOJSONProvider(app)


@app.route("/")
def home():
    return jsonify({"message": "This is Ben's HackerNews custom scraper!"})


@app.route("/api/scrape", methods=["POST"])
def scrape_now():
    # TODO: modify this function, and parse_pages(), to accept a 
    # number which defines how many pages of HN to scrape.
    data = parse_pages(WEBSITES)
    save_scraped_data(data)
    return jsonify({"status": "success"})


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
    return jsonify(articles)


@app.route("/api/keywords", methods=["GET"])
def get_keywords():
    keyword_list = fetch_keywords()
    return jsonify({"keywords": keyword_list})


@app.route("/api/update_keywords", methods=["POST"])
def update_saved_keywords():
    body = request.get_json(silent=True) or {}
    new_keywords = body.get("keywords")
    update_keywords(new_keywords)
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True)


