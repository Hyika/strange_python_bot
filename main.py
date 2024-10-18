import aiohttp
import asyncio
import websockets
import json
import time
from functools import wraps
from threading import Thread


class DiscordBot:
    def __init__(self, json_file_path:str) -> None:
        def load_settings_json(path: str) -> dict:
            with open(path, 'r') as f:
                settings = json.load(f)
            return settings
        
        settings = load_settings_json(path=json_file_path)
        self.base_url = 'https://discord.com/api/v10'
        self.gateway_url = 'wss://gateway.discord.gg/'
        self.token = settings['token']
        self.prefix = settings['command_prefix']
        self.auth_headers = {'Authorization': f'Bot {self.token}'}
        
        self.heartbeat_interval = 0
        self.seq = 0
        self.session_id = None
        self.guild_info = None
    
    class GuildInfo:
        def __init__(self, 
                     guild_id: str,
                     name: str, 
                     channels: list, 
                     members: list, 
                     soundboard_sounds: list, 
                     roles: list, 
                     emojis: list, 
                     stickers: list):
            self.guild_id = guild_id
            self.name = name
            self.channels = channels
            self.members = members
            self.soundboard_sounds = soundboard_sounds
            self.roles = roles
            self.emojis = emojis
            self.stickers = stickers


    async def gateway_connection(self):
        async def connect(f):
            @wraps(wrapper)
            async def wrapper(*args, **kwargs):
                payload = f(*args, **kwargs)
                await websocket.send(json.dumps(payload))
                response = json.loads(await websocket.recv())
                return response
            return wrapper
        
        @connect
        async def establish(websocket: websockets.WebSocketClientProtocol) -> dict:
            payload = {
                'op': 1,
                'd': None,
            }
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return response
        
        async def heartbeat(websocket: websockets.WebSocketClientProtocol) -> dict:
            payload = {
                'op': 1,
                'd': self.seq,
            }
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return response
        
        async def identify(websocket: websockets.WebSocketClientProtocol) -> dict:
            payload = {
                'op': 2, 
                'd': {
                    'token': self.token,
                    'intents': 513,
                    'properties': {
                        'os': 'linux',
                        'browser': 'firefox',
                        'device': 'firefox',
                    },
                    'presence': {
                        'since': None,
                        'activities': [{
                            'name': '리부트서버를 정상화',
                            'type': 0,
                            'state': 'write state.',
                            'url': None, # stream url, is validated when type is 1.
                        }],
                        'status': 'Online', # online, dnd, idle, invisible, offline ...
                        'afk': False,
                    },
                }
            }
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return response

        async def update_presence(websocket:websockets.WebSocketClientProtocol, 
                                  activities: list, 
                                  status: str, 
                                  afk: bool) -> dict:
            payload = {
                'op': 3,
                'd': {
                    'since': None,
                    'activities': activities,
                    'status': status,
                    'afk': afk,
                }
            }
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return response

        async def resume(websocket:websockets.WebSocketClientProtocol) -> dict:
            payload = {
                'op': 6,
                'd': {
                    'token': self.token,
                    'session_id': self.session_id,
                    'seq': self.seq,
                }
            }
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return response

        timestamp = lambda : time.strftime('%y-%m-%d %H:%M:%S')
        error_message = lambda msg: print(f'\033[091m{msg}\033[0m')
        system_mesasge = lambda msg: print(f'\033[092m{msg}\033[0m')

        async with websockets.connect(self.gateway_url) as ws:
            try:
                response = await establish(websocket=ws)
                system_mesasge(f'[{timestamp()}] Establish connection with Gateway.')
                response = await identify(websocket=ws)
                system_mesasge(f'[{timestamp()}] Send Identify with intents.')
                while True:
                    response = json.loads(await ws.recv())
                    opcode = response['op']
                    match opcode:
                        case 0:
                            gateway_event = response['t']
                            match gateway_event:
                                case 'READY':
                                    self.session_id = response['d']['session_id']
                                    self.seq = response['s']
                                    system_mesasge(f'[{timestamp()}] Ready to work')
                                case 'GUILD_CREATE':
                                    data = response['d']
                                    self.guild_info = self.GuildInfo(
                                        guild_id=data['id'],
                                        name=data['name'], 
                                        channels=data['channels'], 
                                        members=data['members'], 
                                        soundboard_sounds=data['soundboard_sounds'], 
                                        roles=data['roles'], 
                                        emojis=data['emojis'], 
                                        stickers=data['stickers'],
                                    )
                                    system_mesasge(f'[{timestamp()}] Succesfully load guild information.')
                        case 7:
                            system_mesasge(f'[{timestamp()}] Reconnecting.')
                            await resume(websocket=ws)
                            system_mesasge(f'[{timestamp()}] Reconnect successful.')
                        case 10:
                            if self.heartbeat_interval == 0:
                                system_mesasge(f'[{timestamp()}] Begin Heartbeat interval.')
                            else:
                                system_mesasge(f'[{timestamp()}] Hello.')
                            self.heartbeat_interval = response['d']['heartbeat_interval']
                            await heartbeat(websocket=ws)
                        case 11:
                            system_mesasge(f'[{timestamp()}] Heartbeat ACK.')
            except Exception as e:
                 error_message(f'[{timestamp()}] {e}')
            finally:
                await ws.close()

    async def send_messages(self, channel_id: str, message: str):
        url = self.base_url+ f'/channels/{channel_id}/messages'
        msg = {'content': message}

        async with aiohttp.ClientSession(headers=bot.auth_headers) as session:
            try:
                async with session.post(url=url, data=msg) as response:
                    response.raise_for_status()
            except Exception as e:
                print(e)
            finally:
                await session.close()


if __name__ == '__main__':
    SETTINGS_JSON = r'user_settings.json'
    bot = DiscordBot(SETTINGS_JSON)
    asyncio.get_event_loop().run_until_complete(bot.gateway_connection())
    asyncio.get_event_loop().close()