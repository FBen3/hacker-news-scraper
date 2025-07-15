import os
import logging

from dotenv import load_dotenv


# Configure for AWS EC2
try:
    import boto3
    BOTO3_AVAILABLE = True

except ImportError:
    BOTO3_AVAILABLE = False


logger = logging.getLogger(__name__)


# Load from .env for local development
load_dotenv()


def get_ssm_parameter(parameter_name):
    """Retrieve config variables from AWS SSM Parameter Store.
    """
    if not BOTO3_AVAILABLE:
        return None
    
    try:
        ssm_client = boto3.client("ssm")
        resp = ssm_client.get_parameter(
            Name=parameter_name,
            WithDescription=True
        )

        return resp["Parameter"]["Value"]
    
    except Exception as e:
        logger.warning(f"Failed to get parameter {parameter_name} from SSM: {e}")
        return None
    

# Detect local or AWS environment
in_aws = os.environ.get("AWS_EXECUTION_ENV") is not None
if in_aws:
    MONGO_ATLAS_URI = get_ssm_parameter("MONGO_ATLAS_URI")
    LOCAL_MONGO_URI = get_ssm_parameter("LOCAL_MONGO_URI")

else:
    MONGO_ATLAS_URI = os.getenv("MONGO_ATLAS_URI")
    LOCAL_MONGO_URI = os.getenv("LOCAL_MONGO_URI")


# Database config
DATABASE_NAME = "hacker_news_scraper_db"
COLLECTION_SCRAPES = "scrapes"
COLLECTION_KEYWORDS = "keywords"


# Scraper config
WEBSITES = [
    "https://news.ycombinator.com",
    "https://news.ycombinator.com/?p=2"
]
