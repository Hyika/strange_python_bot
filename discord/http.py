import asyncio
import aiohttp
import json
import traceback

BOT_VERSION: float = 0.0
API_VERSION: int   = 10

class Route:
    API_BASE_URL: str = "https://discord.com/api/v{API_VERSION}"

    def __init__(self, method: str, path: str, **params: any):
        """
        :method type:
        GET
        POST
        DELETE
        UPDATE
        """
        self.method: str = method
        if params:
            path = path.format_map(params)
        
        self.url = self.base_url + path

    @property
    def base_url(self)-> str:
        return self.API_BASE_URL.format(API_VERSIOM=API_VERSION)


class DiscordHttp:
    def __init__(self, token: str):
        self.__session: aiohttp.ClientSession = None

        self.token = token
        self.user_agent = {
            f"DiscordBot (https://github.com/Hyika/strange_python_bot, {BOT_VERSION})"
        }

    async def request(self, route: Route, **kwargs):
        method = route.method
        url = route.url

        headers: dict[str, str] = {
            "User-Agent": self.__user_agent,
            "Authorization": f"Bot {self.token}",
        }
        if kwargs["data"]:
            headers["Content-Type"] = "application/json"

        return await self.__session.request(method=method, url=url, **kwargs)

    async def create_session(self):
        self.__session = aiohttp.ClientSession()

    async def get_gateway(self):
        response = await self.request(Route("GET", "/Gateway"))
        return "{URL}?v={API_VERSION}&encoding=json".format(
            URL=response["url"],
            API_VERSION=API_VERSION
        )
