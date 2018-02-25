import json
import asyncio
from aiohttp import ClientSession


class BandsInTownRequest:
    """
    A class that implements asynchronous API requests to
    the Bandsintown API
    Usage
    ---------
        request = BandsInTownRequest()
        request.send(artists=['gojira', 'mastodon', 'flying lotus'])
        print(request.results)
    """

    def __init__(self, artists=None):
        self.artists = artists
        self._urls = self.generate_urls()
        self.responses = None
        self.parameters = {
            'app_id': 'concert-react',
            'api_version': '2.0',
            'location': 'Austin, TX',
            'radius': '150',
            'format': 'json'
        }

    def generate_urls(self):
        urls = []
        for artist in self.artists:
            URL = 'http://api.bandsintown.com/artists/'+artist+'/events/search'
            urls.append(URL)
        return urls

    async def send(self):
        """
        The user entry point
        Parameter
        ----------
        location: str
            The name of the location to search for concerts
        """
        await self.run_tasks()

    async def run_tasks(self):
        async with ClientSession() as session:
            tasks = await self.gather_tasks(session)
            self.responses = await asyncio.gather(*tasks)

    async def gather_tasks(self, session):
        tasks = []
        for url in self._urls:
            task = self.schedule_future_event(self.request(url, session))
            tasks.append(task)
        return tasks

    def schedule_future_event(self, coroutine):
        return asyncio.ensure_future(coroutine)

    async def request(self, url, session):
        async with session.get(url, params=self.parameters) as response:
            if response.status != 200:
                raise AttributeError

            data = json.loads(await response.text())
            return self.create_concert(data)

    def create_concert(self, data):
        if data:
            data = data[0]
            concert = {
                'c_id': data['id'],
                'city': data['venue']['city'] + ', ' + data['venue']['region'],
                'title': data['title'],
                'venue': data['venue']['name'],
                'thumb': data['artists'][0]['thumb_url'],
                'artist': data['artists'][0]['name'],
                'tickets': data['ticket_url'],
                'date': data['datetime'],
                'fmt_date': data['formatted_datetime'],
                'ticket_status': data['ticket_status']
            }
            return concert

    @property
    def results(self):
        if self.responses:
            self.clean_up_results()
            return self.responses

    def clean_up_results(self):
        # Removes empty responses
        self.responses = [r for r in self.responses if r is not None]
