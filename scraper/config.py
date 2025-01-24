import os

from dotenv import load_dotenv


load_dotenv()

MONGO_ATLAS_URI = os.getenv("MONGO_ATLAS_URI")
LOCAL_MONGO_URI = os.getenv("LOCAL_MONGO_URI")
DATABASE_NAME = "hacker_news_scraper_db"
COLLECTION_NAME = "scrapes"
