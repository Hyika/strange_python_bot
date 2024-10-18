import aiohttp
import asyncio
import websockets
import json
import time
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
        self.heartbeat_interval = 0

    async def gateway_connection(self):
        def error_mesasge(message: str) -> None:
            print(f'\033[091m{message}\033[0m')
        
        def system_mesasge(message: str) -> None:
            print(f'\033[092m{message}\033[0m')
        
        async def establish(websocket: websockets.WebSocketClientProtocol) -> dict:
            payload = {
                'op': 0,
                'd': None,
            }
            system_mesasge(f'[{time.strftime('%Y-%m-%d %H-%M-%S')}] Establish connection with Gateway.')
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return response
        
        async def heartbeat(websocket: websockets.WebSocketClientProtocol) -> dict:
            payload = {
                'op': 1,
                'd': None,
            }
            system_mesasge('[] Begin Heartbeat interval.')
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
                    }
                }
            }
            system_mesasge('Establish connection with Gateway')
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return response
        
        async def update_presence(websocket:websockets.WebSocketClientProtocol) -> dict:
            payload = {
                'op': 3,
                'd': {
                    'since': None,
                    'activities': [{
                        'name': '신창섭의 정상화',
                        'type': 0,
                        'state': 'write state.',
                        'url': None, # stream url, is validated when type is 1.
                    }],
                    'status': 'Online', # online, dnd, idle, invisible, offline ...
                    'afk': False,
                }
            }
            await websocket.send(json.dumps(payload))
            response = json.loads(await websocket.recv())
            return response

        async with websockets.connect(self.gateway_url) as websocket:
            try:
                response = await establish(websocket=websocket)
                system_mesasge('[Opcode 10] Hello')
                response = await heartbeat(websocket=websocket)
                response = await identify(websocket=websocket)
                response = await update_presence(websocket=websocket)
                if response['op'] == 10:
                    print(system_mesasge('[Opcode 10] Hello'))
                    response = await heartbeat(websocket=websocket)
                    if response['op'] == 11:
                        print('[Opcode 11] Heartbeat ACK')
                        
                        print('Ready!')
                        
            except Exception as e:
                error_mesasge(e)
            finally:
                websocket.close()

            while True:
                response = await heartbeat(websocket=websocket)
                await asyncio.sleep(20)
                print(type(response))


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