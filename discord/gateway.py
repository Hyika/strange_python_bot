import asyncio
import json
import websockets
import traceback

class Gateway:
    def __init__(self, token):
        self.__token = token
        self.url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.session_id = None
        self.heartbeat_interval = None
        self.last_seq_num = None

    async def connect(self)-> None:
        try:
            ws = await websockets.connect(
                uri=self.url, 
                ping_timeout=None,
            )
            self.websocket = ws
        except:
            print("websocket is already connected.")

    async def disconnect(self)-> None:
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        else:
            print("websocket is already disconnected.")

    async def send(self, ws:websockets.WebSocketClientProtocol, payload: dict)-> None:
        await self.websocket.send(json.dumps(payload))
        
    async def receive(self, ws:websockets.WebSocketClientProtocol)-> dict:
        response = json.loads(await self.websocket.recv())
        return response

    # decorator for payload events
    @staticmethod
    def event(func):
        async def wrapper(self, ws:websockets.WebSocketClientProtocol, **kwargs):
            await func(self, ws, **kwargs)
            response = await self.receive(ws=ws)
            return response
        return wrapper
    
    @event
    async def heartbeat(self, ws:websockets.WebSocketClientProtocol)-> dict:
        await self.send(
            ws=ws,
            payload={ "op": 1, "d": None}
        )
    
    @event
    async def identify(self, ws:websockets.WebSocketClientProtocol)-> dict:
        await self.send(
            ws=ws,
            payload={
                "op": 2, 
                "d": {
                    "token": self.__token,
                    "intents": 33281,
                    "properties": {
                        "os": "linux",
                        "$browser": "disco",
                        "$device": "disco",
                    },
                    "presence": {
                        "since": None,
                        "activities": [{
                            "name": "디버깅",
                            "type": 0,
                            "state": "feel so good",
                            "url": None, # stream url, is validated when type is 1.
                        }],
                        "status": "Online", # online, dnd, idle, invisible, offline ...
                        "afk": False,
                    },
                }
            }
        )           

    @event
    async def update_presence(self, ws:websockets.WebSocketClientProtocol, activities: list, status: str, afk: bool)-> dict:
        await self.send(
            ws=ws,
            payload={
                "op": 3,
                "d": {
                    "since": None,
                    "activities": activities,
                    "status": status,
                    "afk": afk,
                }
            }
        )

    @event
    async def resume(self, ws:websockets.WebSocketClientProtocol)-> dict:
        await self.send(
            ws=ws,
            payload={
                "op": 6,
                "d": {
                    "token": minicord.TOKEN,
                    "session_id": self.session_id,
                    "seq": self.last_seq_num
                }
            }
        )
