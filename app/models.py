import datetime

import pymongo

import errors
import settings


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

    @classmethod
    def check_for_none(cls, func):
        def decorator(self, *args):
            item = func(self, *args)
            if item is None:
                raise errors.NotFound
            return item
        return decorator


class TagDatabase(MongoDatabase):
    def create_tag(self, tag):
        tag_exists = self.collection.find_one({"name": tag['name']})
        if tag_exists:
            raise errors.TagAlreadyExists
        self.collection.insert_one(tag)

    @MongoDatabase.check_for_none
    def delete_tag(self, name):
        return self.collection.find_one_and_delete({"name": name})

    @MongoDatabase.check_for_none
    def get_tag(self, name):
        return self.collection.find_one({"name": name})

    def get_all_tags(self):
        return self.collection.find()


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
        document = self.retrieve_artist_listing()
        if document:
            self.update_artist_listing(artists)
        else:
            self.create_artist_listing(artists)

    def remove_artists(self, artists):
        self.validate_removal(artists)
        document = self.retrieve_artist_listing()
        if document:
            self.remove_artist_listing(artists)

    def filter_concerts(self, concerts):
        results = []
        for concert in concerts:
            listing = self.retrieve_concert_listing(concert)
            if not listing:
                self.create_concert_listing(concert)
                results.append(concert)
        return results

    def clean_database(self):
        removed = 0
        date = datetime.datetime.now().isoformat()
        concerts = self.retrieve_all_concert_listings()
        for concert in concerts:
            if concert['date'] < date:
                self.remove_concert_listing(concert)
                removed += 1
        return removed

    def validate_addition(self, artists):
        for artist in artists:
            if artist in self.artists:
                raise errors.DuplicateArtist

    def validate_removal(self, artists):
        for artist in artists:
            if artist not in self.artists:
                raise errors.MissingArtist

    def retrieve_artist_listing(self):
        return self.collection.find_one({'id': self.guild})

    def update_artist_listing(self, artists):
        self.artists += artists
        self.collection.update_one({'id': self.guild}, {"$set": {'artists': self.artists}})

    def create_artist_listing(self, artists):
        self.artists = artists
        documentument = {"id": self.guild, "artists": self.artists}
        self.collection.insert_one(documentument)

    def remove_artist_listing(self, artists):
        self.artists = list(set(self.artists).difference(artists))
        self.collection.update_one({'id': self.guild}, {"$set": {'artists': self.artists}})

    def retrieve_concert_listing(self, concert):
        return self.collection.find_one({'c_id': concert['c_id']})

    def retrieve_all_concert_listings(self):
        return self.collection.find({'c_id': {"$exists": True}})

    def create_concert_listing(self, concert):
        return self.collection.insert_one(concert)

    def remove_concert_listing(self, concert):
        return self.collection.delete_one(concert)

    def get_artists(self):
        self.load_artists()
        return self.artists


class SoundDatabase(MongoDatabase):
    def create_sound(self, sound):
        sound_exists = self.collection.find_one({"name": sound['name']})
        if sound_exists:
            raise errors.SoundAlreadyExists
        self.collection.insert_one(sound)

    @MongoDatabase.check_for_none
    def find_sound(self, name):
        return self.collection.find_one({"name": name})

    @MongoDatabase.check_for_none
    def delete_sound(self, name):
        return self.collection.find_one_and_delete({"name": name})

    def get_all_sounds(self):
        return self.collection.find()

    def used(self, sound):
        count = sound["times_used"] + 1
        self.collection.update_one({'name': sound["name"]}, {"$set": {'times_used': count}})
