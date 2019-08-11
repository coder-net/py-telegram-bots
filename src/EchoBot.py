from BaseBot import BaseBot


class EchoBot(BaseBot):
    def __init__(self, token, loop):
        super().__init__(token, loop)

    @BaseBot.commands.command
    async def echo(self, msg):
        """return sending text"""
        return msg['text'],
