import logging
import json

from scraper import parse_pages
from mongo_db import save_scraped_data
from config import WEBSITES


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    data = parse_pages(WEBSITES)
    save_scraped_data(data)


if __name__ == "__main__":
    main()
