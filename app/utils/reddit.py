from aiohttp import ClientSession, BasicAuth

from settings import REDDIT_CLIENT, REDDIT_SECRET, REDDIT_USER, REDDIT_PASS


class Reddit:
    """Makes API requests to a specified subreddit and returns
    the first ten links sorted by new
    """
    def __init__(self, subreddit=None):
        self.url = f"https://oauth.reddit.com/r/{subreddit}/new.json?limit=10"
        self.user_agent = "TrollScraper/0.1 by Okush"
        self.links = []

    async def __call__(self):
        await self._request_reddit_data()
        return self.links
      
    async def _request_reddit_data(self):
        token = await self._grab_oauth_token()
        token = f"bearer {token}"
        headers = {"Authorization": token, "User-Agent": self.user_agent}
        async with ClientSession() as session:
            async with session.get(self.url, headers=headers) as response:
                json = await response.json()
                reddit_posts = json['data']['children']
                for post in reddit_posts:
                    self.links.append(post['data']['url'])

    async def _grab_oauth_token(self):
        token = BasicAuth(REDDIT_CLIENT, REDDIT_SECRET)
        post_data = {
            'grant_type': "password", "username": REDDIT_USER, 
            "password": REDDIT_PASS
        }
        headers = {"User-Agent": self.user_agent}
        url = "https://www.reddit.com/api/v1/access_token"
        
        async with ClientSession(auth=token) as session:
            async with session.post(url, auth=token, data=post_data, 
                                    headers=headers) as response:
                json = await response.json()
                token = json['access_token']
        return token
