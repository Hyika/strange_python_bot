import aiohttp
import asyncio
import json
import websockets


class minicord:
    def __init__(self, token: str, prefix: str):
        self.token = token
        self.command_prefix = prefix
        self.app = self.App()

    def run(self):
        asyncio.run(self.__execute(self.token))
        """
        "activities": [{
            "name": "디버깅",
            "type": 0,
            "state": "feel so good",
            "url": None, # stream url, is validated when type is 1.
        }],
        "status": "Online", # online, dnd, idle, invisible, offline ...
        "afk": False,
        """
        
    


    async def __execute(self, __token):
        try:
            __gateway = self.Gateway(token=__token)
            ws:websockets.WebSocketClientProtocol = await __gateway.connect()

            response = await __gateway.identify(ws=ws)
            __gateway.heartbeat_interval = response["d"]["heartbeat_interval"]

            while True:
                response = await __gateway.receive(ws=ws)
                
                op = response["op"]
                s  = response["s"]
                t  = response["t"]
                d  = response["d"]

                __gateway.last_seq_num = s

                match t:
                    case "READY":
                        print("Ready!")
                        __gateway.session_id = response["d"]["session_id"]
                    case "GUILD_CREATE":
                        print("Create guild information.")
                        # TODO: write guild create section. 
                    case "MESSAGE_CREATE":
                        print("message create")
                        print(response["d"])
                        if response["d"]["author"]["id"] != "1295320160701382708":
                            # super().send_message(
                            #     channel_id=self.Payload.d["channel_id"],
                            #     content="Pong!",
                            # )
                            print(f"{response["d"]["content"]}")
                    case _:
                        pass

        except KeyboardInterrupt:
            print("Keyborad Interrupt.")
        except Exception as e:
            print(e)
            print("Error")


    class App:
        def __init__(self, command_prefix, application_id):
            self.command_prefix = command_prefix
            self.application_id = application_id
            self.command = self.Commands(self.command_prefix)

        class Commands:
            def __init__(self, command_prefix):
                self.command_prefix = command_prefix

            @staticmethod
            def command(name):
                def decorator(func):
                    async def wrapper(self, ctx):

                        await func(self, ctx)


bot = minicord()
bot.run()