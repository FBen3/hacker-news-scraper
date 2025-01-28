"""Database Logic

The database connection code and helper functions
for intereacting with the database go in here. 

"""
from contextlib import contextmanager
from datetime import datetime
import json

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from config import (
    MONGO_ATLAS_URI,
    DATABASE_NAME,
    COLLECTION_NAME
)


@contextmanager
def connect_database():
    """Create a context manager for database connections"""
    client = MongoClient(MONGO_ATLAS_URI, server_api=ServerApi('1'))

    try:
        yield client[DATABASE_NAME]
    finally:
        client.close()


def fetch_saved_articles(date=None):
    """Get every saved article by default; filter by date if provided"""
    with connect_database() as db:
        collection = db[COLLECTION_NAME]

        pipeline = []  # initialize pipeline
        if date:
            pipeline.append(
                {"$match": {"scrape_date": {"$regex": f"^{date}"}}}  # match documents with a date if present
            )
        pipeline.append({"$unwind": "$saves"})  # unwind the saves array
        pipeline.append({"$replaceRoot": {"newRoot": "$saves"}})  # project only article detials

        all_articles = list(collection.aggregate(pipeline))

        return json.dumps(all_articles, indent=4)


def get_original_save_date(title):
    """Get the original scrape date of an article"""
    db = connect_database()
    collection = db[COLLECTION_NAME]

    original_document = collection.find_one(
        {"saves.title": title},  # query
        {"scrape_date": 1, "_id": 0}  # projection
    )

    return original_document["scrape_date"]


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
    update_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

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

        collection.insert_one(data)
        # should I log a message if empty? Or if only an update happened?


def fetch_duplicate_titles(data, date):
    """Return articles already in the database"""
    current_titles = {article["title"] for article in data["saves"]}

    with connect_database() as db:
        collection = db[COLLECTION_NAME]

        pipeline = [
            {"$match": {"scrape_date": {"$regex": f"^{date}"}}},  # match documents for a specific date
            {"$unwind": "$saves"},  # unwind saved articles
            {"$project": {"_id": 0, "title": "$saves.title"}}  # filter for only the title field
        ]
        result = collection.aggregate(pipeline)

        past_titles = {article["title"] for article in result}
        duplicates = current_titles & past_titles

        return duplicates


def save_scraped_data(data):
    """Save scraped data into collection"""
    if not data:
        print("No data to insert. Try again.")
        return
    
    with connect_database() as db:
        collection = db[COLLECTION_NAME]

        # check if database is empty for that day
        # IF non-empty -> check for duplicates
        # ELSE -> insert data right away
        today = datetime.now().strftime('%Y-%m-%d')
        query = {"scrape_date": {"$regex": f"^{today}"}}

        if collection.count_documents(query) > 0:
            duplicates = fetch_duplicate_titles(data, today)
            insert_data(data, duplicates)

        else:
            insert_data(data)


if __name__ == "__main__":
    sample_data_1 = {}
    save_scraped_data(sample_data_1)
    # save_scraped_data(sample_data_2)
    # save_scraped_data(sample_data_3)
    # print(fetch_all_saved_articles())
