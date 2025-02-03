import logging

from scraper import parse_pages
from config import WEBSITES


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    parse_pages(WEBSITES)


if __name__ == "__main__":
    main()
