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
        self.auth_headers = {
            'Authorization': f'Bot {self.token}',
        }
        self.auth_headers = {
            'Authorization': f'Bot {self.token}',
        }
        
        self.last_sent_opcode = -1
        self.last_sent_opcode = -1
        self.heartbeat_interval = 0
        self.seq = 0
        self.application_id = None
        self.application_id = None
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
        async def establish(websocket: websockets.WebSocketClientProtocol) -> dict:
            payload = {
                'op': 1,
                'd': None,
            }
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return [websocket, payload]
        
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
        error_message = lambda msg: print(f'\033[091m[{timestamp()}] {msg}\033[0m')
        system_mesasge = lambda msg: print(f'\033[092m[{timestamp()}] {msg}\033[0m')
        error_message = lambda msg: print(f'\033[091m[{timestamp()}] {msg}\033[0m')
        system_mesasge = lambda msg: print(f'\033[092m[{timestamp()}] {msg}\033[0m')

        async with websockets.connect(self.gateway_url, ping_timeout=None) as ws:
        async with websockets.connect(self.gateway_url, ping_timeout=None) as ws:
            try:
                response = await establish(websocket=ws)
                system_mesasge(f'Establish connection with Gateway.')
                system_mesasge(f'Establish connection with Gateway.')
                response = await identify(websocket=ws)
                system_mesasge(f'Send Identify with intents.')
                system_mesasge(f'Send Identify with intents.')
                while True:
                    response = json.loads(await ws.recv())
                    opcode = response['op']
                    match opcode:
                        case 0:
                            gateway_event = response['t']
                            match gateway_event:
                                case 'READY':
                                    await self.send_messages('1023644509168484413', 'ya feel so good')
                                    self.application_id = response['d']['application']['id']
                                    await self.send_messages('1023644509168484413', 'ya feel so good')
                                    self.application_id = response['d']['application']['id']
                                    self.session_id = response['d']['session_id']
                                    self.seq = response['s']
                                    system_mesasge(f'Ready to work')
                                    system_mesasge(f'Ready to work')
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
                                    system_mesasge('Succesfully load guild information.')
                                    system_mesasge('Succesfully load guild information.')
                        case 7:
                            system_mesasge('Reconnecting.')
                            system_mesasge('Reconnecting.')
                            await resume(websocket=ws)
                            system_mesasge(f'Reconnect successful.')
                        case 9:
                            error_message('Invalid session.')
                            
                            if self.last_sent_opcode == 2:
                                error_message('the gateway could not initialize a session after receiving an Opcode 2 Identify.')
                            elif self.last_sent_opcode == 6:
                                error_message('the gateway could not resume a previous session after receiving an Opcode 6 Resume.')
                            else:
                                error_message('the gateway has invalidated an active session and is requesting client action.')
                        
                            if response['d']:
                                system_mesasge('Reconnecting.')
                                await resume(websocket=ws)
                                system_mesasge(f'Reconnect successful.')
                            else:
                                system_mesasge('Session closed.')
                                # 수정 예정
                            system_mesasge(f'Reconnect successful.')
                        case 9:
                            error_message('Invalid session.')
                            
                            if self.last_sent_opcode == 2:
                                error_message('the gateway could not initialize a session after receiving an Opcode 2 Identify.')
                            elif self.last_sent_opcode == 6:
                                error_message('the gateway could not resume a previous session after receiving an Opcode 6 Resume.')
                            else:
                                error_message('the gateway has invalidated an active session and is requesting client action.')
                        
                            if response['d']:
                                system_mesasge('Reconnecting.')
                                await resume(websocket=ws)
                                system_mesasge(f'Reconnect successful.')
                            else:
                                system_mesasge('Session closed.')
                                # 수정 예정
                        case 10:
                            if self.heartbeat_interval == 0:
                                system_mesasge('Begin Heartbeat interval.')
                                system_mesasge('Begin Heartbeat interval.')
                            else:
                                system_mesasge('Hello.')
                                system_mesasge('Hello.')
                            self.heartbeat_interval = response['d']['heartbeat_interval']
                            await heartbeat(websocket=ws)
                        case 11:
                            system_mesasge('Heartbeat ACK.')
                            system_mesasge('Heartbeat ACK.')
            except Exception as e:
                 error_message(f'{e}')
                 error_message(f'{e}')
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