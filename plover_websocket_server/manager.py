from typing import Optional, List

from plover.engine import StenoEngine
from plover.steno import Stroke
from plover.config import Config
from plover.formatting import _Action
from plover.steno_dictionary import StenoDictionaryCollection
from plover_websocket_server.server import (WebSocketServer, ServerStatus,
                                            ERROR_SERVER_RUNNING, ERROR_NO_SERVER)


ERROR_MISSING_ENGINE = 'Plover engine not provided to web socket server'

class WebSocketServerManager():
    '''
    Manages a server that exposes Plover events via Websockets
    '''

    def __init__(self, engine: StenoEngine):
        self._server: Optional[WebSocketServer] = None
        self._engine: StenoEngine = engine

    def start(self):
        '''
        Called to start the server.
        '''

        if self.get_server_status() != ServerStatus.Stopped:
            raise AssertionError(ERROR_SERVER_RUNNING)

        self._server = WebSocketServer()
        self._server.start()

        self._connect_hooks()

    def stop(self):
        '''
        Called to stop the server.
        '''

        if not self._server or self.get_server_status() != ServerStatus.Running:
            raise AssertionError(ERROR_NO_SERVER)

        self._disconnect_hooks()

        self._server.queue_stop()
        self._server.join()
        self._server = None

    def get_server_status(self) -> ServerStatus:
        '''
        Gets the status of the server.

        :return: The status of the server.
        '''

        return self._server.status if self._server else ServerStatus.Stopped

    def _connect_hooks(self):
        '''
        Creates hooks into all of Plover's events.
        '''

        if not self._engine:
            raise AssertionError(ERROR_MISSING_ENGINE)

        self._engine.hook_connect('stroked', self._on_stroked)
        self._engine.hook_connect('translated', self._on_translated)
        self._engine.hook_connect('machine_state_changed', self._on_machine_state_changed)
        self._engine.hook_connect('output_changed', self._on_output_changed)
        self._engine.hook_connect('config_changed', self._on_config_changed)
        self._engine.hook_connect('dictionaries_loaded', self._on_dictionaries_loaded)
        self._engine.hook_connect('send_string', self._on_send_string)
        self._engine.hook_connect('send_backspaces', self._on_send_backspaces)
        self._engine.hook_connect('send_key_combination', self._on_send_key_combination)
        self._engine.hook_connect('add_translation', self._on_add_translation)
        self._engine.hook_connect('focus', self._on_focus)
        self._engine.hook_connect('configure', self._on_configure)
        self._engine.hook_connect('lookup', self._on_lookup)
        self._engine.hook_connect('quit', self._on_quit)

    def _disconnect_hooks(self):
        '''
        Removes hooks from all of Plover's events.
        '''

        if not self._engine:
            raise AssertionError(ERROR_MISSING_ENGINE)

        self._engine.hook_disconnect('stroked', self._on_stroked)
        self._engine.hook_disconnect('translated', self._on_translated)
        self._engine.hook_disconnect('machine_state_changed', self._on_machine_state_changed)
        self._engine.hook_disconnect('output_changed', self._on_output_changed)
        self._engine.hook_disconnect('config_changed', self._on_config_changed)
        self._engine.hook_disconnect('dictionaries_loaded', self._on_dictionaries_loaded)
        self._engine.hook_disconnect('send_string', self._on_send_string)
        self._engine.hook_disconnect('send_backspaces', self._on_send_backspaces)
        self._engine.hook_disconnect('send_key_combination', self._on_send_key_combination)
        self._engine.hook_disconnect('add_translation', self._on_add_translation)
        self._engine.hook_disconnect('focus', self._on_focus)
        self._engine.hook_disconnect('configure', self._on_configure)
        self._engine.hook_disconnect('lookup', self._on_lookup)
        self._engine.hook_disconnect('quit', self._on_quit)

    def _on_stroked(self, stroke: Stroke):
        '''
        Called when a new stroke is performed.

        :param stroke: The stroke that was just performed.
        '''

        data = {'stroked': {
            'stroke': stroke.rtfcre,
            'keys': stroke.steno_keys
        }}
        self._server.queue_message(data)

    def _on_translated(self, old: List[_Action], new: List[_Action]):
        '''
        Called when a new translation occurs.

        :param old: A list of the previous actions for the current translation.
        :param new: A list of the new actions for the current translation.
        '''

        # TODO: Need to do more than a string conversion eventually
        data = {
            'translated': {
                'old': str(old),
                'new': str(new)
            }}
        self._server.queue_message(data)

    def _on_machine_state_changed(self, machine_type: str, machine_state: str):
        '''
        Called when the active machine state changes.

        :param machine_type: The name of the active machine.
        :param machine_state: The new machine state. This should be one of the
                              state constants listed in plover.machine.base.
        '''

        data = {
            'machine_state_changed': {
                'machine_type': machine_type,
                'machine_state': machine_state
            }}
        self._server.queue_message(data)

    def _on_output_changed(self, enabled: bool):
        '''
        Called when the state of output changes.

        :param enabled: If the output is now enabled or not.
        '''

        data = {'output_changed': enabled}
        self._server.queue_message(data)

    def _on_config_changed(self, config_update: Config):
        '''
        Called when the configuration changes.

        :param config_update: An object containing the full configuration or
                              a part of the configuration that was updated.
        '''

        # TODO: This is probably not sufficient for all cases and some converting
        #       of the data for sending has to happen?
        data = {'config_changed': config_update}
        self._server.queue_message(data)

    def _on_dictionaries_loaded(self, dictionaries: StenoDictionaryCollection):
        '''
        Called when all of the dictionaries get loaded.

        :param dictionaries: A collection of the dictionaries that loaded.
        '''

        # TODO: Need to do more than a string conversion eventually
        data = {'dictionaries_loaded': str(dictionaries)}
        self._server.queue_message(data)

    def _on_send_string(self, text: str):
        '''
        Called when a new string is output.

        :param text: The string that was output.
        '''

        data = {'send_string': text}
        self._server.queue_message(data)

    def _on_send_backspaces(self, count: int):
        '''
        Called when backspaces are output.

        :parm count: The number of backspaces that were output.
        '''

        data = {'send_backspaces': count}
        self._server.queue_message(data)

    def _on_send_key_combination(self, combination: str):
        '''
        Called when a key combination is output.

        :param combination: A string representing a sequence of key combinations.
                            Keys are represented by their names based on the OS-
                            specific keyboard implementations in plover.oslayer.
        '''

        data = {'send_key_combination': combination}
        self._server.queue_message(data)

    def _on_add_translation(self):
        '''.
        Called when the add translation tool is opened via a command.
        '''

        data = {'add_translation': True}
        self._server.queue_message(data)

    def _on_focus(self):
        '''
        Called when the main window is focused via a command.
        '''

        data = {'focus': True}
        self._server.queue_message(data)

    def _on_configure(self):
        '''
        Called when the configuration tool is opened via a command.
        '''

        data = {'configure': True}
        self._server.queue_message(data)

    def _on_lookup(self):
        '''
        Called when the lookup tool is opened via a command.
        '''

        data = {'lookup': True}
        self._server.queue_message(data)

    def _on_quit(self):
        '''
        Called when the application is terminated.
        Can be either a full quit or a restart.
        '''

        data = {'quit': True}
        self._server.queue_message(data)
