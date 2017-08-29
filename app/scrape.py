import json
import time
import pymongo
import requests
import settings
from config import logger


# Data Model
# Concert = {"_id": event['id'],
#            "title" : event['title'],
#            "date": event['formatted_datetime'],
#            "artist": event['artists'][0]['name'],
#            "image": event['artists'][0]['image_url']}

def find_all_concerts():
    """
    Use BandsinTown API to search for concert events
    """
    client = pymongo.MongoClient(settings.DB_URL)
    db = client.settings.DB_NAME
    concerts = db['concerts']
    results = []

    for art in settings.ARTISTS:
        URL = settings.BIT_URL + art + '/events/search'

        param = {'app_id': settings.ID, 'api_version': settings.API,
                 'location': settings.LOCATION, 'radius': settings.RADIUS,
                 'format': 'json'}

        resp = requests.get(URL, params=param )

        if resp.status_code != 200:
            raise ApiError('{} response code'.format(resp.status_code))

        # Load JSON data from response
        json_data = json.loads(resp.text)

        old_result_found = 0
        new_results_found = 0
        for event in json_data:
            # Query the database to compare current listing to any
            # that already exists
            concert = concerts.find_one({'_id': event['id']})

            if concert:
                old_result_found += 1
            else:
                concert = {
                    "_id": event['id'],
                    "title": event['title'],
                    "date": event['formatted_datetime'],
                    'artist': event['artists'][0]['name'],
                    'image': event['artists'][0]['image_url']
                }
                concerts.insert_one(concert)
                new_results_found += 1
                results.append(concert)

        if json_data == []:
            logger.info(f'Found No Results For {art}')

        if json_data:
            logger.info(f'Found {old_result_found} posted result and ' 
                        f'{new_results_found} new results for {art}')
    logger.info("Scrape was completed")
    client.close()
    return results


class ApiError(Exception):
    pass
