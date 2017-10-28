import logging
import daiquiri
import pymongo
import settings

# Setup logger
daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()

# Database Context Manager
class ConnectDatabase:
    def __init__(self, guild):
        self.guild = guild
        self.client = pymongo.MongoClient(settings.DB_URL)
        self.db = self.client.settings.DB_NAME
        self.collection = self.db[guild]
    
    def __enter__(self):
        return self.collection

    def __exit__(self, type, value, traceback):
        self.client.close()