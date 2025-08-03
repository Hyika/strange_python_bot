import aiohttp
import asyncio
import websockets
import json
import time


# bot main
class DiscordBot:
    def __init__(self):
        self.guild = None
        
    def run(self):
        Client.run()
    
    class UserSetting:
        with open(r'./user_setting.json', 'r') as f:
            user_setting = json.load(f)

        TOKEN = user_setting['token']
        PREFIX = user_setting['command_prefix']

    class Guild:
        def __init__(self, guild_data:dict):
            self.activity_instances = guild_data['activity_instances']
            self.afk_channel_id = guild_data['afk_channel_id']
            self.afk_timeout = guild_data['afk_timeout']
            self.application_command_counts = guild_data['application_command_counts']
            self.application_id = guild_data['application_id']
            self.banner = guild_data['banner']
            self.channels = self.channel_tree(guild_data['channels'])

        def channel_tree(self, channels: list):
            parent_channels = []
            for channel in channels:
                parent_id = channel.get('parent_id')
                if parent_id is None:   # parent channel
                    parent_channel = self.Channel(channel_data=channel)
                    parent_channels.append(parent_channel)
                else:                   # child channel
                    for parent_channel in parent_channels:
                        if parent_channel.id == parent_id:
                            if channel.get('bitrate') is None:
                                text_channel = self.Channel.TextChannel(text_chl_data=channel)
                                parent_channel.child_text_channel.append(text_channel)
                            else:
                                voice_channel = self.Channel.VoiceChanel(voice_chl_data=channel)
                                parent_channel.child_voice_channel.append(voice_channel)
            
            return parent_channels

        class Channel:
            def __init__(self, channel_data):
                self.flags = channel_data['flags']
                self.id = channel_data['id']
                self.name = channel_data['name']
                self.permission_overwrites = channel_data['permission_overwrites']
                self.position = channel_data['position']
                self.type = channel_data['type']
                self.version = channel_data['version']
                self.child_text_channel = []
                self.child_voice_channel = []

            class TextChannel:
                def __init__(self, text_chl_data):
                    self.default_thread_rate_limit_per_user = text_chl_data['default_thread_rate_limit_per_user']
                    self.flags = text_chl_data['flags']
                    self.icon_emoji = text_chl_data['icon_emoji']
                    self.id = text_chl_data['id']
                    self.last_message_id = text_chl_data['last_message_id']
                    self.name = text_chl_data['name']
                    self.parent_id = text_chl_data['parent_id']
                    self.permission_overwrites = text_chl_data['permission_overwrites'] # dict
                    self.position = text_chl_data['position']
                    self.rate_limit_per_user = text_chl_data['rate_limit_per_user']
                    self.topic = text_chl_data['topic']
                    self.type = text_chl_data['type']
                    self.version = text_chl_data['version']

            class VoiceChanel:
                def __init__(self, voice_chl_data):
                    self.bitrate = voice_chl_data['bitrate']
                    self.flags = voice_chl_data['flags']
                    self.icon_emoji = voice_chl_data['icon_emoji'] # dict
                    self.id = voice_chl_data['id']
                    self.last_message_id = voice_chl_data['last_message_id']
                    self.name = voice_chl_data['name']
                    self.parent_id = voice_chl_data['parent_id']
                    self.permission_overwrites = voice_chl_data['permission_overwrites']
                    self.position = voice_chl_data['position']
                    self.rate_limit_per_user = voice_chl_data['rate_limit_per_user']
                    self.rtc_region = voice_chl_data['rtc_region']
                    self.type = voice_chl_data['type']
                    self.user_limit = voice_chl_data['user_limit']
                    self.version = voice_chl_data['version']

class Client(DiscordBot):
    def __init__(self):
        super().__init__()

    @staticmethod
    def run():
        gateway = GatewayConnection()
        asyncio.run(gateway.connect())

    @staticmethod
    def message(msg, tag:str=None):
        match tag:
            case 'gateway_send':
                color = '\033[092m'
            case 'gateway_recv':
                color = '\033[093m'
            case 'error':
                color = '\033[091m'
            case 'bot_recv':
                color = '\033[094m'
            case _:
                color = '\033[0m'

        print((f'{color}[{time.strftime('%y-%m-%d %H:%M:%S')}] {msg}\033[0m'))

class GatewayConnection:
    def __init__(self):
        self.gateway_url = 'wss://gateway.discord.gg/?v=10&encoding=json'
        self.heartbeat_interval = 0
        self.websocket = None
        self.payload = self.EventPayload()
        self.session_id = None

    async def connect(self):
        self.websocket = await websockets.connect(self.gateway_url, ping_timeout=None)
        Client.message(msg='[-->] Create websocket and establish connection with Gateway.', tag='gateway_send')
        await self.receive()

        await self.send(self.EventPayload.heartbeat())
        Client.message(msg='[-->] Begin Heartbeat interval', tag='gateway_send')
        await self.receive()

        await self.send(self.EventPayload.identify(DiscordBot.UserSetting.TOKEN))
        Client.message(msg='[-->] Send Identify with intents.', tag='gateway_send')
        await self.receive()

        await self.send(self.EventPayload.heartbeat())
        Client.message(msg='[-->] Send Guild information.', tag='gateway_send')
        await self.receive()

        while True:
            await self.receive()

    async def close(self):
        await self.websocket.close()
    
    async def send(self, payload):
        await self.websocket.send(json.dumps(payload))

    async def receive(self):
        payload = json.loads(await self.websocket.recv())
        #print(payload)

        op = payload['op']
        s = payload['s']
        t = payload['t']
        d = payload['d']

        match op:
            case 0:
                if t == 'READY':
                    
                elif t == 'GUILD_CREATE':
                    #self.guild = Client.Guild(d)

                elif t == 'MESSAGE_CREATE':
                    current_channel_id = d['channel_id']
                    member_info = d['member']
                    #event
            case 1:
                self.send(self.EventPayload.heartbeat())
            case 10:
                Client.message(msg='[<--] Received Hello event.', tag='gateway_recv')
                self.heartbeat_interval = d['heartbeat_interval']
            case 11:
                Client.message(msg='[<--] Received Heartbeat ACK event.', tag='gateway_recv')
    
    class Events:
        @classmethod
        def event(cls, received_event, received_data):
            match received_event:
                case 'READY':
                    Client.message(msg='[<--] Received Ready event.', tag='gateway_recv')
                    cls.ready(session_id=received_data['session_id'],
                              resume_gateway_url=received_data['resume_gateway_url'])
                case 'GUILD_CREATE':
                    Client.message(msg='[<--] GUILD CREATE.', tag='bot_recv')
                    cls.guild_create()
                case 'MESSAGE_CREATE':
                    Client.message(msg='[<--] MESSAGE CREATE.', tag='bot_recv')
                    cls.message_create()

        def ready(self, session_id:str, resume_gateway_url:str):
            self.session_id = session_id
            self.gateway_url = resume_gateway_url

        def guild_create(self):
            DiscordBot.Guild.channel_tree
        

    class EventPayload:
        def __init__(self, op:int=-1, s:int=None, t:str=None, d:any=None):
            self.__opcode = op
            self.__seq_num = s
            self.__event_name = t
            self.__event_data = d

        def is_empty(self):
            if self.__opcode == -1:
                return True
            elif self.__opcode > -1:
                return False
            else:
                raise Exception

        @property
        def getter(self):
            payload = {
                'op': self.__opcode,
                's': self.__seq_num,
                't': self.__event_name,
                'd': self.__event_data,
            }
            return payload
        
        @getter.setter
        def setter(self, payload:dict):
            self.__opcode = payload['op']
            self.__seq_num = payload['s']
            self.__event_name = payload['t']
            self.__event_data = payload['d']

        @staticmethod
        def heartbeat(last_seq_num:int=None):
            payload = {
                'op': 1,
                'd': last_seq_num
            }
            return payload
        
        @staticmethod
        def identify(token):
            payload = {
                'op': 2, 
                'd': {
                    'token': token,
                    'intents': 513,
                    'properties': {
                        'os': 'linux',
                        'browser': 'disco',
                        'device': 'disco',
                    },
                    'presence': {
                        'since': None,
                        'activities': [{
                            'name': '디버깅',
                            'type': 0,
                            'state': 'feel so good',
                            'url': None, # stream url, is validated when type is 1.
                        }],
                        'status': 'Online', # online, dnd, idle, invisible, offline ...
                        'afk': False,
                    },
                }
            }
            return payload
            
        @staticmethod
        def update_presence(activities: list, status: str, afk: bool):
            payload = {
                'op': 3,
                'd': {
                    'since': None,
                    'activities': activities,
                    'status': status,
                    'afk': afk,
                }
            }
            return payload

        @staticmethod
        def resume(last_seq:int, last_session_id:int):
            payload = {
                'op': 6,
                'd': {
                    'token': DiscordBot.UserSetting.TOKEN,
                    'session_id': last_session_id,
                    'seq': last_seq
                }
            }
            return payload
    
class HttpConnection:
    def __init__(self):
        self.connect = None




if __name__ == '__main__':
    bot = DiscordBot()
    bot.run()