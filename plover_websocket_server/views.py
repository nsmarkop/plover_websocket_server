from aiohttp import web, WSMsgType


async def index(request: web.Request) -> web.Response:
    '''
    Index endpoint for the server. Not really needed.

    :param request: The request from the client.
    '''

    return web.Response(text='index')

async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    '''
    The main WebSocket handler.

    :param request: The request from the client.
    '''

    print('WebSocket connection starting')
    socket = web.WebSocketResponse()
    await socket.prepare(request)
    request.app['websockets'].append(socket)
    print('WebSocket connection ready')

    async for message in socket:
        print(message)
        if message.type == WSMsgType.TEXT:
            print(message.data)

            if message.data == 'close':
                await socket.close()
        elif message.type == WSMsgType.ERROR:
            print(f'WebSocket connection closed with exception {socket.exception()}')

    request.app['websockets'].remove(socket)
    print('WebSocket connection closed')
    return socket
