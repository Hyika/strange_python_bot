import asyncio
import aiohttp
import json
import traceback


class HTTP:
    def __init__(self, token):
        self.__token = token
        self.api_url = "https://discord.com/api/v10"
        self.header = {
            "Authorization": f"Bot {self.__token}",
            "Content-Type": "application/json",
        }
    
    @staticmethod
    def restAPI(func):
        async def wrapper(self, session, **kwargs):
            async with aiohttp.ClientSession(headers=self.header) as session:
                response = await func(self, session, **kwargs)
                return response
            return wrapper

    @restAPI
    async def get(self, session, url)-> dict:
        async with session.get(url) as response:
            return response.json(encoding="UTF-8")
    
    @restAPI
    async def post(self, session, url, data)-> None:
        async with session.post(url=url, data=json.dumps(data)) as response:
            return response.json(encoding="UTF-8")

    async def disconnect(self)-> None:
        if self.session:
            await self.session.close()
            self.session = None
        else:
            print("session is already disconnected.")
