import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


# Scrapper configuration
CEFR_LEVEL_ORDER = {
    'A1': 1,
    'A2': 2,
    'B1': 3,
    'B2': 4,
    'C1': 5,
    'C2': 6,
}

SCRAPPER_SETTINGS = {
    'USER_AGENT': 'language-learning-app',
    'LOG_LEVEL': 'ERROR',
}


# Database environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
