"""Database Logic

The database connection code and helper functions
for intereacting with the database go in here. 

"""
from contextlib import contextmanager
from datetime import datetime, timedelta
import logging
import json
from typing import List

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError
from pydantic import BaseModel, ValidationError

from config import (
    MONGO_ATLAS_URI,
    DATABASE_NAME,
    COLLECTION_NAME
)


logger = logging.getLogger(__name__)


# Article model
class ArticleRecord(BaseModel):
    matched_keywords: List[str]
    title: str
    points: int
    post_date: datetime
    url: str
    number_of_comments: int | None


# Scrape Data model
class ScrapeResult(BaseModel):
    scrape_date: datetime
    saves: List[ArticleRecord] = []


@contextmanager
def connect_database():
    """Create a database client, closing it upon exit.
    Any DB errors are intended to bubble up by deafult.
    """
    client = None
    try:
        client = MongoClient(MONGO_ATLAS_URI, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # check if database is reachable
        yield client[DATABASE_NAME]

    finally:
        if client is not None:
            client.close()


def fetch_saved_articles(date=None):
    """Get every saved article by default; filter by date if provided"""
    try:
        with connect_database() as db:
            collection = db[COLLECTION_NAME]

            pipeline = []  # initialize pipeline
            if date:
                start_of_day = datetime(date.year, date.month, date.day)  # mindnight
                end_of_day = start_of_day + timedelta(days=1)  # next midnight

                pipeline.append(
                    {"$match": {"scrape_date": {"$gte": start_of_day, "$lt": end_of_day}}}
                )
            pipeline.append({"$unwind": "$saves"})  # unwind the saves array
            pipeline.append({"$replaceRoot": {"newRoot": "$saves"}})  # project only article detials

            all_articles = list(collection.aggregate(pipeline))

            return json.dumps(all_articles, indent=4)
        
    except PyMongoError as e:
        logger.error(f"[MongoDB] Failed to fetch saved articles: {e}")
        return json.dumps({"error": "Database query failed for some reason!"})


def get_original_save_date(title):
    """Get the original scrape date of an article"""
    try:    
        with connect_database() as db:
            collection = db[COLLECTION_NAME]

            original_document = collection.find_one(
                {"saves.title": title},  # query
                {"scrape_date": 1, "_id": 0}  # projection
            )

            if not original_document:
                logger.warning(f"[MongoDB] No original save date found for: {title}")
                return None

            return original_document["scrape_date"]
        
    except PyMongoError as e:
        logger.error(f"[MongoDB] Failed to get original scrape date for: {title}. Error {e}")
        return None


def update_existing_article(article, title, original_date, update_date, collection):
    """Helper function to update existing article metadata"""
    collection.update_one(
        {"scrape_date": original_date, "saves.title": title},
        {
            "$set": {
                "saves.$.points": article["points"],
                "saves.$.comments": article["number_of_comments"],
                "saves.$.updated_at": update_date                 
            }
        }
    )


def insert_data(data, duplicates=None):
    """Insert new articles; update saved ones"""
    update_date = datetime.now()

    try:
        with connect_database() as db:    
            collection = db[COLLECTION_NAME]

            if duplicates:
                de_dupped_articles = [
                    article for article in data["saves"] if article["title"] not in duplicates
                ]

                for article in data["saves"]:
                    title = article["title"]
                    if article["title"] in duplicates:
                        original_date = get_original_save_date(title=title)
                        update_existing_article(article, title, original_date, update_date, collection)

                data["saves"] = de_dupped_articles
                logger.info(f"Updated {len(duplicates)} existing articles in database")

            collection.insert_one(data)
            logger.info(f"Inserted {len(data["saves"])} new articles in database")

    except PyMongoError as e:
        logger.error(f"[MongoDB] Failed to insert/update data: {e}")


def fetch_duplicate_titles(data, date):
    """Return articles already in the database"""
    current_titles = {article["title"] for article in data["saves"]}

    try:
        with connect_database() as db:
            collection = db[COLLECTION_NAME]

            start_of_day = datetime(date.year, date.month, date.day)
            end_of_day = start_of_day + timedelta(days=1)

            pipeline = [
                {"$match": {"scrape_date": {"$gte": start_of_day, "$lt": end_of_day}}},  # match documents for a specific date
                {"$unwind": "$saves"},  # unwind saved articles
                {"$project": {"_id": 0, "title": "$saves.title"}}  # filter for only the title field
            ]
            result = collection.aggregate(pipeline)

            past_titles = {article["title"] for article in result}

            return current_titles & past_titles
        
    except PyMongoError as e:
        logger.error(f"[MongoDB] Failed to fetch duplicate titles: {e}")
        return set()


def save_scraped_data(data):
    """Save scraped data into collection after validation"""
    try:
        valid_data = ScrapeResult.model_validate(data)
        logger.info("Scrape data validation successful.")

        with connect_database() as db:
            collection = db[COLLECTION_NAME]

            # check if database is empty for that day
            # IF not empty -> check for duplicates
            # ELSE -> insert data right away
            today = datetime.now()
            start_of_day = datetime(today.year, today.month, today.day)
            end_of_day = start_of_day + timedelta(days=1)

            query = {"scrape_date": {"$gte": start_of_day, "$lt": end_of_day}}

            if collection.count_documents(query) > 0:
                duplicates = fetch_duplicate_titles(valid_data.model_dump(), today)
                insert_data(valid_data.model_dump(), duplicates)
                logger.info(f"Scraped data for {today.strftime('%Y-%m-%d')}. {len(duplicates)} duplicates found.")
            else:
                insert_data(valid_data.model_dump())
                logger.info(f"Scraped data for {today.strftime('%Y-%m-%d')}")

    except ValidationError as e:
        logger.error(f"[Pydantic] Invalid scraped data format: {e}")

    except PyMongoError as e:
        logger.error(f"[From MongoDB] Failed to save scraped data: {e}")


if __name__ == "__main__":
    sample_data_1 = {}
    save_scraped_data(sample_data_1)
    # save_scraped_data(sample_data_2)
    # save_scraped_data(sample_data_3)
    # print(fetch_all_saved_articles())
