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
        ssm_client = boto3.client("ssm", region_name="us-east-1")
        resp = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )

        return resp["Parameter"]["Value"]
    
    except Exception as e:
        logger.warning(f"Failed to get parameter {parameter_name} from SSM: {e}")
        return None
    

def get_config_value(ssm_param, env_var):
    """Try SSM, fall back to environment variable.
    """
    value = get_ssm_parameter(ssm_param)
    if value:
        logger.info(f"Using {ssm_param} from SSM Parameter Store")
        return value
    
    value = os.getenv(env_var)
    if value:
        logger.info(f"Using {env_var} from environment variable")
        return value
    
    logger.warning(f"Could not find {ssm_param} in SSM or {env_var} in environment")
    return None


# Fetch configuration values
MONGO_ATLAS_URI = get_config_value("MONGO_ATLAS_URI", "MONGO_ATLAS_URI")
LOCAL_MONGO_URI = get_config_value("LOCAL_MONGO_URI", "LOCAL_MONGO_URI")


# Database config
DATABASE_NAME = "hacker_news_scraper_db"
COLLECTION_SCRAPES = "scrapes"
COLLECTION_KEYWORDS = "keywords"


# Scraper config
WEBSITES = [
    "https://news.ycombinator.com",
    "https://news.ycombinator.com/?p=2"
]
