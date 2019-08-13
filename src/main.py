import asyncio
import aiohttp
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from EchoBot import EchoBot


client = AsyncIOMotorClient('localhost', 27017)
redis = asyncio.get_event_loop().run_until_complete(aioredis.create_connection(('localhost', 6379)))
echo_bot_token = '891848363:AAGjabMFNvi61DJ1dQ8C3BCH6he92EbXG_U'

def init_app(bots):
    app = aiohttp.web.Application()
    for bot in bots:
        app.router.add_post('/bots/{}'.format(bot._token), bot.handler)
    return app

def main():
    loop = asyncio.get_event_loop()

    bots = [
        EchoBot(echo_bot_token, loop, redis),
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
