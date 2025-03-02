from pymongo import MongoClient
from constants import MONGO_URI
from functools import lru_cache


@lru_cache(maxsize=1)
def get_mongo_instance():
    """
    Get MongoDB connection with LRU caching
    :return: MongoDB connection
    """
    client = MongoClient(MONGO_URI)
    db = client["documents_db"]
    return db
