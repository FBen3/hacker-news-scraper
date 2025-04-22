import logging

from src.scraper.config import WEBSITES
from src.scraper.scraper import parse_pages
from src.scraper.mongo_db import save_scraped_data


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    data = parse_pages(WEBSITES)
    save_scraped_data(data)


if __name__ == "__main__":
    main()
