"""Database Logic

The database connection code and helper functions
for intereacting with the database go in here. 

"""
from datetime import datetime

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from config import (
    MONGO_ATLAS_URI,
    DATABASE_NAME,
    COLLECTION_NAME
)


def connect_database():
    """Establish connection to MongoDB and return the database object"""
    client = MongoClient(MONGO_ATLAS_URI, server_api=ServerApi('1'))

    return client[DATABASE_NAME]
    # client.close() ???


def get_original_save_date(title):
    """Get the original scrape date of an article"""
    db = connect_database()
    collection = db[COLLECTION_NAME]

    original_document = collection.find_one(
        {"saves.title": title},  # query
        {"scrape_date": 1, "_id": 0}  # projection
    )

    return original_document["scrape_date"]


def insert_data(data, duplicates=None):
    """Only insert articles not already scraped"""
    de_dupped_articles = []
    update_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    db = connect_database()
    collection = db[COLLECTION_NAME]

    if duplicates:
        for article in data["saves"]:
            title = article["title"]
            if title in duplicates:
                original_date = get_original_save_date(title=title)
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
            else:
                de_dupped_articles.append(article)

        data["saves"] = de_dupped_articles
  
    collection.insert_one(data)


def fetch_duplicates(data, date):
    """Return articles already in the database"""
    current_titles = {article["title"] for article in data["saves"]}

    # get titles of all the ones already in db
    db = connect_database()
    collection = db[COLLECTION_NAME]

    pipeline = [
        {"$match": {"scrape_date": {"$regex": f"^{date}"}}},  # match documents for a specific date
        {"$unwid": "$saves"},  # unwind saved articles
        {"$project": {"_id": 0, "title": "$saves.title"}}  # filter for only the title field
    ]
    result = collection.aggregate(pipeline)

    past_titles = [article["title"] for article in result]
    duplicates = current_titles & past_titles

    return duplicates


def save_scraped_data(data):
    """Save scraped data into collection"""
    if not data:
        print("No data to insert. Try again.")
        return
    
    db = connect_database()
    collection = db[COLLECTION_NAME]

    # check if database is empty for that day
    # IF non-empty -> check for duplicates
    # ELSE -> insert data right away
    today = datetime.now().strftime('%Y-%m-%d')
    query = {"scrape_date": {"$regex": f"^{today}"}}

    if collection.count_documents(query) > 0:
        duplicates = fetch_duplicates(data, today)
        insert_data(data, duplicates)

    else:
        insert_data(data)
   


if __name__ == "__main__":
    sample_data = {
        "scrape_date": "2024-08-29T17:51:54",
        "saves": [
            {
                "matched_keywords": ["BCI"],
                "title": "Something BCI",
                "points": 412,
                "post_date": "2024-08-29T17:51:54",
                "url": "https://blog.kagi.com/dawn-new-era-search",
                "number_of_comments": 6
            },
            {
                "matched_keywords": ["Neuro"],
                "title": "Something Neuro",
                "points": 412,
                "post_date": "2024-08-29T17:51:54",
                "url": "https://blog.kagi.com/dawn-new-era-search",
                "number_of_comments": 6
            }
        ]
    }
    save_scraped_data(sample_data)






