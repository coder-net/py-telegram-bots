import asyncio
import aiohttp
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from EchoBot import EchoBot
from JournalBot import JournalBot


client = AsyncIOMotorClient('localhost', 27017)
echo_bot_token = '891848363:AAGjabMFNvi61DJ1dQ8C3BCH6he92EbXG_U'
journal_bot_token = '739416851:AAHuFJ1-xt4fD7xXhSh8YaeehaHGx9xzY1c'

def init_app(bots):
    app = aiohttp.web.Application()
    for bot in bots:
        app.router.add_post('/bots/{}'.format(bot._token), bot.handler)
    return app

def main():
    loop = asyncio.get_event_loop()
    redis = loop.run_until_complete(aioredis.create_connection(('localhost', 6379)))

    bots = [
        EchoBot(echo_bot_token, loop, redis),
        JournalBot(journal_bot_token, loop, redis, client[journal_bot_token]),
    ]

    try:
        aiohttp.web.run_app(init_app(bots))
    except BaseException as exc:
        print(exc)
    finally:
        for bot in bots:
            bot.shutdown()


if __name__ == '__main__':
    main()
