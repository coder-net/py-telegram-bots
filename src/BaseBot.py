import aiohttp
from Commands import Commands


class BaseBot:
    URL = 'https://api.telegram.org/bot{token}/{method}'

    def __init__(self, token, loop):
        self._token = token
        self._loop = loop
        self._session = aiohttp.ClientSession()

    def shutdown(self):
        self._session.close()

    async def _post_request(self, method, params=None, data=None):
        async with self._session.post(self.URL.format(token=self._token, method=method), data=data, params=params) as resp:
            try:
                assert resp.status == 200
            except AssertionError:
                print('Some problems')

    async def handler(self, request):
        msg = await request.json()
        self._loop.create_task(self._handler(msg))
        return aiohttp.web.Response(status=200)

    async def _handler(self, msg):
        command = msg['message']['text'].split(maxsplit=2)[0]
        res = await self.commands.find_command(command)(self, msg['message'])
        await self.send_message(msg['message']['chat']['id'], *res)

    async def send_message(self, chat_id, msg, params={}):
        data = {'chat_id': chat_id, 'text': msg}
        data.update(params)
        await self._post_request('sendMessage', params=data)

    #TODO solve problen with unknown and using BaseBot.commands.command decorator without BaseBot
    async def unknown(self, msg):
        file_id = "CAADAgADJQIAAs4XpwtUsH1SVc8NDxYE"
        await self._post_request('sendSticker', params={
            'chat_id': msg['chat']['id'],
            'sticker': file_id
        })
        return 'Unknown command. Use /help',

    commands = Commands(unknown)

    @commands.command
    async def help(self, msg):
        """get info about bot commands"""
        res = ''
        for command, func in self.commands.commands.items():
            res += f'{command} - _{func.__doc__}_\n'
        return res, {'parse_mode': 'Markdown'}