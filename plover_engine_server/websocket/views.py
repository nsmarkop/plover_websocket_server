"""The views / handlers for the server."""

from aiohttp import web, WSMsgType


async def index(request: web.Request) -> web.Response:
    """Index endpoint for the server. Not really needed.

    Args:
        request: The request from the client.
    """

    return web.Response(text='index')


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    """The main WebSocket handler.

    Args:
        request: The request from the client.
    """

    print('WebSocket connection starting', flush=True)
    socket = web.WebSocketResponse()
    await socket.prepare(request)
    request.app['websockets'].append(socket)
    print('WebSocket connection ready', flush=True)

    async for message in socket:
        if message.type == WSMsgType.TEXT:
            if message.data == 'close':
                await socket.close()
        elif message.type == WSMsgType.ERROR:
            print('WebSocket connection closed with exception '
                  f'{socket.exception()}', flush=True)

    request.app['websockets'].remove(socket)
    print('WebSocket connection closed', flush=True)
    return socket
