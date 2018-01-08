import logging
import datetime
import daiquiri
import pymongo
import settings
import errors

# Setup logger
daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()

# Database Context Manager
class MongoDatabase:
    def __init__(self, guild):
        self.guild = guild
        self.client = pymongo.MongoClient(settings.DB_URL)
        self.db = self.client.settings.DB_NAME
        self.collection = self.db[guild]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.client.close()

class TagDatabase(MongoDatabase):
    def check_for_none(func):
        def decorator(self, *args):
            tag = func(self, *args)
            if tag is None:
                raise errors.NoTagFound
            return tag
        return decorator

    def create_tag(self, tag):
        tag_exists = self.collection.find_one({"name": tag['name']})
        if tag_exists:
            raise errors.TagAlreadyExists
        self.collection.insert_one(tag)

    def get_all_tags(self):
        return self.collection.find()
    
    @check_for_none
    def get_tag(self, name):
        return self.collection.find_one({"name": name})
    
    @check_for_none    
    def delete_tag(self, name):
        return self.collection.find_one_and_delete({"name": name})
    
class ConcertDatabase(MongoDatabase):
    def __init__(self, guild):
        super().__init__(guild)
        self.artists = self.load_artists()
    
    def load_artists(self):
        query = self.collection.find_one({"id": self.guild})
        if query:
            return [a for a in query['artists']]
        else:
            return []
    
    def add_artists(self, artists):
        self.validate_addition(artists)
        doc = self.retrieve_artist_document()
        if doc:
            self.update_artist_document(artists)
        else:
            self.create_artist_document(artists)
    
    def validate_addition(self, artists):
        for artist in artists:
            if artist in self.artists:
                raise errors.DuplicateArtist
        return 

    def retrieve_artist_document(self):
        return self.collection.find_one({'id': self.guild})

    def update_artist_document(self, artists):
        self.artists += artists
        self.collection.update_one({'id': self.guild}, {"$set": {'artists': self.artists}})
    
    def create_artist_document(self, artists):
        self.artists = artists
        document = {"id": self.guild, "artists": self.artists}   
        self.collection.insert_one(document)
    
    def remove_artists(self, artists):
        self.validate_removal(artists)
        doc = self.retrieve_artist_document()
        if doc:
            self.remove_from_artist_document(artists)
    
    def validate_removal(self, artists):
        for artist in artists:
            if artist not in self.artists:
                raise errors.MissingArtist
        return
    
    def remove_from_artist_document(self, artists):
        self.artists = list(set(self.artists).difference(artists))
        self.collection.update_one({'id': self.guild}, {"$set": {'artists': self.artists}})
    
    def filter_concerts(self, concerts):
        results = []
        for concert in concerts:
            listing = self.retrieve_concert_listing(concert)
            if not listing:
                self.create_concert_listing(concert)
                results.append(concert)
        return results
    
    def retrieve_concert_listing(self, concert):
        return self.collection.find_one({'c_id': concert['c_id']})

    def create_concert_listing(self, concert):
        return self.collection.insert_one(concert)

    def remove_concert_listing(self, concert):
        return self.collection.delete_one(concert)
    
    def clean_database(self):
        removed = 0
        date = datetime.datetime.now().isoformat()
        concerts = self.retrieve_all_concert_listings()
        for concert in concerts:
            if concert['date'] < date:
                self.remove_concert_listing(concert)
                removed += 1
        return removed

    def retrieve_all_concert_listings(self):
        return self.collection.find({'c_id': {"$exists": True}})

    def get_artists(self):
        self.load_artists()
        return self.artists
    