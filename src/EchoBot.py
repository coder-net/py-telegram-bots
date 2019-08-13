from BaseBot import BaseBot


class EchoBot(BaseBot):
    def __init__(self, token, loop, redis):
        self._redis = redis
        super().__init__(token, loop)

    async def _handler(self, msg):
        chat_id = msg['message']['chat']['id']
        next_command = await self._db_next_command(chat_id)
        if 'text' in msg['message']:
            command = msg['message']['text'].split(maxsplit=2)[0]
            func = self.commands.find_command(command)
            if func:
                await self._db_del_next_command(chat_id)
        if not func and next_command:
            func = self.commands.find_system_command(next_command.decode('utf-8'))
        func = func or BaseBot.unknown
        res = await func(self, msg['message'])
        await self.send_message(chat_id, *res)

    async def _db_del_next_command(self, chat_id):
        await self._redis.execute('hdel', self._token, chat_id)

    async def _db_next_command(self, chat_id):
        return await self._redis.execute('hget', self._token, chat_id)

    async def _db_set_next_command(self, chat_id, command):
        await self._redis.execute('hset', self._token, chat_id, command)

    @BaseBot.commands.command
    async def echo(self, msg):
        """return sending text"""
        return msg['text']

    @BaseBot.commands.command
    async def sticker(self, msg):
        """return sticker `file id`"""
        await self._db_set_next_command(msg['chat']['id'], 'sticker_id')
        return 'Okey. Send me sticker to know its file_id',

    @BaseBot.commands.system_command
    async def sticker_id(self, msg):
        if 'sticker' in msg:
            await self._db_del_next_command(msg['chat']['id'])
            return msg['sticker']['file_id'],
        return "This's not sticker. Please, send sticker",

