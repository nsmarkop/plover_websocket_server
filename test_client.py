import asyncio

import aiohttp
from plover_websocket_server.server import DEFAULT_HOST, DEFAULT_PORT


URL = f'http://{DEFAULT_HOST}:{DEFAULT_PORT}/websocket'

async def main():
    session = aiohttp.ClientSession()

    async with session.ws_connect(URL) as socket:
        async for message in socket:
            if message.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                break

            print('data: ', message.data)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
