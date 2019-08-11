import asyncio
import aiohttp
from EchoBot import EchoBot


def init_app(bots):
    app = aiohttp.web.Application()
    for bot in bots:
        app.router.add_post('/bots/{}'.format(bot._token), bot.handler)
    return app


def main():
    loop = asyncio.get_event_loop()

    bots = [
        EchoBot('891848363:AAGjabMFNvi61DJ1dQ8C3BCH6he92EbXG_U', loop),
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
