"""Core engine server definitions."""

from enum import Enum, auto
from threading import Thread
import asyncio


class ServerStatus(Enum):
    """Represents the status of the server.

    Attributes:
        Stopped: The server is stopped.
        Running: The server is running.
    """

    Stopped = auto()
    Running = auto()


class EngineServer(Thread):
    """A server for the Plover engine.

    Attributes:
        status: The current status of the server.
    """

    def __init__(self, host: str, port: str):
        """Initialize the server.

        Args:
            host: The host address for the server to run on.
            port: The port for the server to run on.
        """

        super().__init__(target=self._start)

        self._host = host
        self._port = port

        self._loop = None
        self.status: ServerStatus = ServerStatus.Stopped

    def queue_message(self, data: dict):
        """Queues a message for the server to broadcast.

        Assumes it is called from a thread different from the event loop.

        Args:
            data: The data in JSON format to broadcast.
        """

        if not self._loop:
            return

        asyncio.run_coroutine_threadsafe(self._broadcast_message(data),
                                         self._loop)

    def queue_stop(self):
        """Queues the server to stop.

        Assumes it is called from a thread different from the event loop.
        """

        if not self._loop:
            return

        asyncio.run_coroutine_threadsafe(self._stop(), self._loop)

    def _start(self):
        """Starts the server.

        Will create a blocking event loop.
        """

        raise NotImplementedError()

    async def _stop(self):
        """Stops the server.

        Performs any clean up operations as needed.
        """

        raise NotImplementedError()

    async def _broadcast_message(self, data: dict):
        """Broadcasts a message to connected clients.

        Args:
            data: The data in JSON format to broadcast.
        """

        raise NotImplementedError()
