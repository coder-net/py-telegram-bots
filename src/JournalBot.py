import asyncio
from BaseBot import BaseBot
from Commands import Commands


class JournalBot(BaseBot):
    commands = Commands()
    _time_units = {
        's': 1,
        'm': 60,
        'h': 3600,
    }

    def __init__(self, token, loop, redis, db):
        self._redis = redis
        self._db = db
        super().__init__(token, loop, self.__class__)

    async def _handler(self, msg):
        chat_id = msg['message']['chat']['id']
        next_command = await self._redis_get_next_command(chat_id)
        func = None
        if 'text' in msg['message']:
            command = msg['message']['text'].split(maxsplit=2)[0]
            func = self.commands.find_command(command)
            if func:
                await self._redis_del_next_command(chat_id)
        if not func and next_command:
            func = self.commands.find_system_command(next_command.decode('utf-8'))
        func = func or BaseBot.unknown
        res = await func(self, msg['message'])
        await self.send_message(chat_id, *res)

    # method for work with redis (maybe changed)
    async def _redis_set_next_command(self, chat_id, command):
        await self._redis.execute('hset', self._token, chat_id, command)

    async def _redis_get_next_command(self, chat_id):
        return await self._redis.execute('hget', self._token, chat_id)

    async def _redis_del_next_command(self, chat_id):
        await self._redis.execute('hdel', self._token, chat_id)

    # method for work with db (mongodb, motor)
    # async def _mongo_update_command(self, chat_id, type, dict):
    #     pass

    # commands
    @commands.command
    async def timer(self, msg):
        """set interval timer"""
        await self._redis_set_next_command(msg['chat']['id'], 'set_timer')
        return (('Okey. Send duration\n'
                 'For time unit you can use `m` - minute, `h` - hour, `s` - second\n'
                 'For example: `1 h`, `15m`, `90 s`'),
                self.markdown)

    @commands.system_command
    async def set_timer(self, msg):
        def parse_time(s):
            for i in range(len(s)):
                if s[i] != ' ' and not s[i].isdigit():
                    return s[:i].strip(), s[i:].strip()
            return '', ''

        if 'text' not in msg:
            return 'Message doesn\'t contain duration. Please, send again',
        duration, time_unit = parse_time(msg['text'])
        time_unit = time_unit or 'm'
        try:
            duration = float(duration)
        except ValueError:
            return 'Incorrect duration. Please, send integer number',

        if time_unit not in self._time_units:
            return 'Incorrect time unit. Please, use `s`, `m`, `h`', {'parse_mode': 'Markdown'}
        await self._redis_set_next_command(msg['chat']['id'], 'set_timer_description')
        await self._db[msg['chat']['id'].__str__()].timer.update_one({'type': 'timer'}, {'$set': {'duration': duration, 'time_unit': time_unit}}, upsert=True)
        return 'Okey. Send description for your business',

    @commands.system_command
    async def set_timer_description(self, msg):
        sticker_id = 'CAADAgADFwIAAs4XpwuZ4fJ0ryIJuBYE'
        if 'text' not in msg:
            return 'Message doesn\'t contain description. Please, send again',
        chat_id, description = msg['chat']['id'], msg['text']

        doc = await self._db[chat_id.__str__()].timer.find_one({'type': 'timer'})
        duration, time_unit = doc['duration'], doc['time_unit']

        await self.send_sticker(chat_id, sticker_id)
        self._loop.create_task(self.end_timer(chat_id, duration * self._time_units[time_unit],  description))
        await self._redis_del_next_command(chat_id)
        return 'Okey. You have `{} {}` to do `{}`.\nI\'ll send you message, when time end'.format(duration, time_unit, description), self.markdown

    async def end_timer(self, chat_id, duration, description):
        sticker_id = 'CAADAgADIwIAAs4XpwsWWIe0wW11KhYE'
        await asyncio.sleep(duration)
        await self.send_sticker(chat_id, sticker_id)
        await self.send_message(chat_id, 'Wake up. Your time for `{}` has ended'.format(description), {'parse_mode': 'Markdown'})

    @commands.command
    async def add(self, msg):
        """add business to list"""
        await self._redis_set_next_command(msg['chat']['id'], 'add_to_db')
        return 'Okey. Send me description',

    @commands.system_command
    async def add_to_db(self, msg):
        sticker_id = 'CAADAgADEwIAAs4XpwszVsmUnLtc8BYE'
        if 'text' not in msg:
            return 'Message doesn\'t contain text. Please, send description'
        chat_id = msg['chat']['id']
        await self._db[chat_id.__str__()].list.insert_one({'description': msg['text']})
        await self._redis_del_next_command(chat_id)
        await self.send_sticker(chat_id, sticker_id)
        return '`{}` added to list'.format(msg['text']), self.markdown

    @commands.command
    async def list(self, msg):
        """return list of your businesses"""
        docs = self._db[msg['chat']['id'].__str__()].list.find()
        res = 'Your list:\n'
        for i, doc in enumerate(await docs.to_list(None), 1):
            res += '_{}._ `{}`\n'.format(i, doc['description'])
        return res, self.markdown

    @commands.command
    async def delete(self, msg):
        """delete business from list"""
        chat_id = msg['chat']['id']
        func = self.commands.find_command('/list')
        await self._redis_set_next_command(chat_id, 'delete_from_db')
        res = 'Okey. Send number of business to delete\n\n' + (await func(self, msg))[0]
        return res, self.markdown

    @commands.system_command
    async def delete_from_db(self, msg):
        chat_id = msg['chat']['id']
        if 'text' not in msg:
            return 'Message doesn\'t contain number',
        try:
            n = int(msg['text'])
        except ValueError:
            return 'Not a number. Send again',
        docs = self._db[chat_id.__str__()].list.find()
        for i, doc in enumerate(await docs.to_list(None), 1):
            if i == n:
                await self._db[chat_id.__str__()].list.delete_one({'_id': doc['_id']})
                await self._redis_del_next_command(chat_id)
                return 'Deleted successfully',
        return 'Number out of range. Try again',
