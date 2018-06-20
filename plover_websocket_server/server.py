from enum import Enum, auto
from threading import Thread
import asyncio

from aiohttp import web, WSCloseCode
from plover_websocket_server.routes import setup_routes


ERROR_SERVER_RUNNING: str = 'A server is already running'
ERROR_NO_SERVER: str = 'A server is not currently running'
DEFAULT_HOST: str = 'localhost'
DEFAULT_PORT: int = 8086

class ServerStatus(Enum):
    '''
    An enum representing the current state of the server
    '''

    Stopped = auto()
    Running = auto()

class WebSocketServer(Thread):
    '''
    A server that uses WebSockets
    '''

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        '''
        :param host: The host address for the server to run on.
        :param port: The port for the server to run on.
        '''

        super().__init__(target=self._start)

        self._app = None
        self._host = host
        self._port = port

        self.status = ServerStatus.Stopped

    def _start(self):
        '''
        Runs the server in a blocking loop.
        '''

        if self.status == ServerStatus.Running:
            raise AssertionError(ERROR_SERVER_RUNNING)

        # We're in the thread process so it's safe to set our event
        # loop to a new one that we're creating now
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self._app = web.Application()
        self._app['websockets'] = []

        setup_routes(self._app)
        self._app.on_shutdown.append(self._on_server_shutdown)

        self.status = ServerStatus.Running
        web.run_app(self._app, host=self._host, port=self._port)

    def queue_message(self, data: dict):
        '''
        Queues a message to be broadcast by the server's event loop.
        Assumes it is being called from a thread different from the event loop.

        :param data: The data in JSON format to broadcast.
        '''

        # Don't queue a message if we don't have a server running. This can happen
        # when hooks connect before the server thread has finished starting
        if not self._app:
            return

        asyncio.run_coroutine_threadsafe(self._broadcast_message(data), self._app.loop)

    def queue_stop(self):
        '''
        Queues the server to stop.
        Assumes it is being called from a thread different from the event loop.
        '''

        # Don't try to stop the server if we don't have a server running.
        # This should never happen, but...
        if not self._app:
            return

        asyncio.run_coroutine_threadsafe(self._stop(), self._app.loop)

    async def _stop(self):
        '''
        Called to stop the server.
        '''

        if self.status != ServerStatus.Running:
            raise AssertionError(ERROR_NO_SERVER)

        self._app.loop.stop()

        await self._app.shutdown()
        await self._app.cleanup()

        self._app = None
        self.status = ServerStatus.Stopped

    async def _on_server_shutdown(self, app: web.Application):
        '''
        Handles pre-shutdown behavior for the server.
        '''

        for socket in app.get('websockets', []):
            await socket.close(code=WSCloseCode.GOING_AWAY,
                               message='Server shutdown')

    async def _broadcast_message(self, data: dict):
        '''
        Broadcasts a message to every connected websocket.

        :param data: The data in JSON format to broadcast.
        '''

        for socket in self._app.get('websockets', []):
            try:
                await socket.send_json(data)
            except:
                print('Failed to update websocket')
