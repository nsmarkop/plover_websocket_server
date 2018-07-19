"""The middleman between Plover and the server."""

from typing import Optional, List
import os
import json

import jsonpickle

from plover.engine import StenoEngine
from plover.steno import Stroke
from plover.config import Config, CONFIG_DIR
from plover.formatting import _Action
from plover.steno_dictionary import StenoDictionaryCollection

from plover_engine_server.errors import (
    ERROR_MISSING_ENGINE,
    ERROR_SERVER_RUNNING,
    ERROR_NO_SERVER
)
from plover_engine_server.server import (
    EngineServer,
    ServerStatus
)
from plover_engine_server.websocket.server import WebSocketServer
from plover_engine_server.config import ServerConfig


SERVER_CONFIG_FILE = 'plover_engine_server_config.json'


class EngineServerManager():
    """Manages a server that exposes the Plover engine."""

    def __init__(self, engine: StenoEngine):
        self._server: Optional[EngineServer] = None
        self._engine: StenoEngine = engine
        self._config_path: str = os.path.join(CONFIG_DIR, SERVER_CONFIG_FILE)

    def start(self):
        """Starts the server.

        Raises:
            AssertionError: The server failed to start.
            IOError: The server failed to start.
        """

        if self.get_server_status() != ServerStatus.Stopped:
            raise AssertionError(ERROR_SERVER_RUNNING)

        config = ServerConfig(self._config_path)

        self._server = WebSocketServer(config.host, config.port)
        self._server.start()

        # TODO: Wait until the server actually starts before connecting hooks
        self._connect_hooks()

    def stop(self):
        """Stops the server.

        Raises:
            AssertionError: The server failed to stop.
        """

        if self.get_server_status() != ServerStatus.Running:
            raise AssertionError(ERROR_NO_SERVER)

        self._disconnect_hooks()

        self._server.queue_stop()
        self._server.join()
        self._server = None

    def get_server_status(self) -> ServerStatus:
        """Gets the status of the server.

        Returns:
            The status of the server.
        """

        return self._server.status if self._server else ServerStatus.Stopped

    def _connect_hooks(self):
        """Creates hooks into all of Plover's events."""

        if not self._engine:
            raise AssertionError(ERROR_MISSING_ENGINE)

        for hook in self._engine.HOOKS:
            callback = getattr(self, f'_on_{hook}')
            self._engine.hook_connect(hook, callback)

    def _disconnect_hooks(self):
        """Removes hooks from all of Plover's events."""

        if not self._engine:
            raise AssertionError(ERROR_MISSING_ENGINE)

        for hook in self._engine.HOOKS:
            callback = getattr(self, f'_on_{hook}')
            self._engine.hook_disconnect(hook, callback)

    def _on_stroked(self, stroke: Stroke):
        """Broadcasts when a new stroke is performed.

        Args:
            stroke: The stroke that was just performed.
        """

        stroke_json = jsonpickle.encode(stroke, unpicklable=False)

        data = {'stroked': json.loads(stroke_json)}
        self._server.queue_message(data)

    def _on_translated(self, old: List[_Action], new: List[_Action]):
        """Broadcasts when a new translation occurs.

        Args:
            old: A list of the previous actions for the current translation.
            new: A list of the new actions for the current translation.
        """

        old_json = jsonpickle.encode(old, unpicklable=False)
        new_json = jsonpickle.encode(new, unpicklable=False)

        data = {
            'translated': {
                'old': json.loads(old_json),
                'new': json.loads(new_json)
            }
        }
        self._server.queue_message(data)

    def _on_machine_state_changed(self, machine_type: str, machine_state: str):
        """Broadcasts when the active machine state changes.

        Args:
            machine_type: The name of the active machine.
            machine_state: The new machine state. This should be one of the
                state constants listed in plover.machine.base.
        """

        data = {
            'machine_state_changed': {
                'machine_type': machine_type,
                'machine_state': machine_state
            }
        }
        self._server.queue_message(data)

    def _on_output_changed(self, enabled: bool):
        """Broadcasts when the state of output changes.

        Args:
            enabled: If the output is now enabled or not.
        """

        data = {'output_changed': enabled}
        self._server.queue_message(data)

    def _on_config_changed(self, config_update: Config):
        """Broadcasts when the configuration changes.

        Args:
            config_update: An object containing the full configuration or a
                part of the configuration that was updated.
        """

        config_json = jsonpickle.encode(config_update, unpicklable=False)

        data = {'config_changed': json.loads(config_json)}
        self._server.queue_message(data)

    def _on_dictionaries_loaded(self, dictionaries: StenoDictionaryCollection):
        """Broadcasts when all of the dictionaries get loaded.

        Args:
            dictionaries: A collection of the dictionaries that loaded.
        """

        dictionaries_json = jsonpickle.encode(dictionaries, unpicklable=False)

        data = {'dictionaries_loaded': json.loads(dictionaries_json)}
        self._server.queue_message(data)

    def _on_send_string(self, text: str):
        """Broadcasts when a new string is output.

        Args:
            text: The string that was output.
        """

        data = {'send_string': text}
        self._server.queue_message(data)

    def _on_send_backspaces(self, count: int):
        """Broadcasts when backspaces are output.

        Args:
            count: The number of backspaces that were output.
        """

        data = {'send_backspaces': count}
        self._server.queue_message(data)

    def _on_send_key_combination(self, combination: str):
        """Broadcasts when a key combination is output.

        Args:
            combination: A string representing a sequence of key combinations.
                Keys are represented by their names based on the OS-specific
                keyboard implementations in plover.oslayer.
        """

        data = {'send_key_combination': combination}
        self._server.queue_message(data)

    def _on_add_translation(self):
        """Broadcasts when the add translation tool is opened via a command."""

        data = {'add_translation': True}
        self._server.queue_message(data)

    def _on_focus(self):
        """Broadcasts when the main window is focused via a command."""

        data = {'focus': True}
        self._server.queue_message(data)

    def _on_configure(self):
        """Broadcasts when the configuration tool is opened via a command."""

        data = {'configure': True}
        self._server.queue_message(data)

    def _on_lookup(self):
        """Broadcasts when the lookup tool is opened via a command."""

        data = {'lookup': True}
        self._server.queue_message(data)

    def _on_quit(self):
        """Broadcasts when the application is terminated.

        Can be either a full quit or a restart.
        """

        data = {'quit': True}
        self._server.queue_message(data)
