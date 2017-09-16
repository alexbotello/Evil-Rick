import logging
import daiquiri
import pymongo
import settings
from contextlib import contextmanager

# Setup logger
daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()

# Database Context Manager
@contextmanager
def connect_database(guild):
    """ Connect to database """
    client = pymongo.MongoClient(settings.DB_URL)
    db = client.settings.DB_NAME
    collection = db[guild]
    yield collection
    client.close()
    