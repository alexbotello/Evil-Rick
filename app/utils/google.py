from aiohttp import ClientSession
from bs4 import BeautifulSoup


class GoogleSearch:
    def __init__(self, query):
        self.url = "http://www.google.com/search?hl=en&safe=off&q="
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7)' \
                     'Gecko/2009021910 Firefox/3.0.7'
        self.header = {'User-Agent':self.user_agent}
        self.query = query.replace(' ', '+')
    
    async def __call__(self):
        response = await self.request()
        raw_url = self.parse_response(response)
        url = self.format_url(raw_url)
        link = self.replace_seperators(url)
        return link
    
    async def request(self):
        url = self.url + self.query
        async with ClientSession() as session:
            async with session.get(url, headers=self.header) as resp:
                response = await resp.text()
        return response

    def parse_response(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        for item in soup.find_all('div', {'class': 'g'}):
            url = item.find('a', href=True)['href'].replace('/url?q=', '')
            break
        return url

    def format_url(self, url):
        if '&sa' in url:
            link = ''
            for char in url:
                if '&sa' in link:
                    break
                else:
                    link += char
            url = link.replace('&sa', '')
        return url

    def replace_seperators(self, url):
        seperators = {'%3F': '?' , '%3D': '=', '%2520': '%20'}
        for key, val in seperators.items():
            if key in url:
                url = url.replace(key, val)
        return url