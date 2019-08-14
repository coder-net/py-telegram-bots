import aiohttp
from Commands import Commands


class BaseBot:
    URL = 'https://api.telegram.org/bot{token}/{method}'
    commands = Commands()
    markdown = {'parse_mode': 'Markdown'}

    def __init__(self, token, loop, cls):
        self._token = token
        self._loop = loop
        self._session = aiohttp.ClientSession()
        BaseBot._set_required_methods(cls)

    def _set_required_methods(cls):
        cls.start = cls.commands.command(cls.start)
        cls.help = cls.commands.command(cls.help)

    async def shutdown(self):
        await self._session.close()

    async def handler(self, request):
        msg = await request.json()
        self._loop.create_task(self._handler(msg))
        return aiohttp.web.Response(status=200)

    async def _handler(self, msg):
        command = msg['message']['text'].split(maxsplit=2)[0]
        func = (self.commands.find_command(command) or BaseBot.unknown)
        res = await func(self, msg['message'])
        await self.send_message(msg['message']['chat']['id'], *res)

    async def _post_request(self, method, params=None, data=None):
        async with self._session.post(self.URL.format(token=self._token, method=method), data=data, params=params) as resp:
            try:
                assert resp.status == 200
            except AssertionError:
                print('Some problems', resp.status, await resp.json())

    async def send_message(self, chat_id, msg, params={}):
        data = {'chat_id': chat_id, 'text': msg}
        data.update(params)
        await self._post_request('sendMessage', params=data)

    async def send_sticker(self, chat_id, file_id, params={}):
        data = {'chat_id': chat_id, 'sticker': file_id}
        data.update(params)
        await self._post_request('sendSticker', params=data)

    async def unknown(self, msg):
        file_id = "CAADAgADFQIAAs4Xpwu3KX9oj5ycyBYE"  # file_id for sticker
        await self.send_sticker(msg['chat']['id'], file_id)
        return 'Unknown command. Use /help',

    async def help(self, msg):
        """get info about bot commands"""
        res = ''
        for command, func in self.commands.commands.items():
            res += f'{command} - _{func.__doc__}_\n'
        return res, self.markdown

    async def start(self, msg):
        """send first message, when user start conversation"""
        res = await self.help(msg)
        return f"Hello, I\'m {self.__class__.__name__}. See my commands:\n" + res[0], res[1]