# Plover WebSocket Server

A WebSocket server for exposing [Plover](https://github.com/openstenoproject/plover) events.

This is currently under development and has the following known issues / limitations:

- The server doesn't actually shut down when disabling the extension via the GUI and will only stop once Plover is completely closed.
- The server doesn't handle disabling / enabling again properly
- There are probably some issues with threads; I just create them and don't care about / join them later currently
- The host and port are not currently configurable and will always try to be on localhost:8086
- Various unintended exceptions get logged when sending socket data at the moment, though they don't seem to have a functional impact? Probably due to certain data not properly mapping to JSON for sending

## Installation

TODO: This will be true once released. For now, you can only pip install this from source which requires running Plover from source to use.

Download the latest version of Plover for your operating system from the [releases page](https://github.com/openstenoproject/plover/releases). Only versions 4.0.0.dev8 and higher are supported.

1. Open Plover
2. Navigate to the Plugin Manager tool
3. Select the "plover-websocket-server" plugin entry in the list
4. Click install
5. Restart Plover

The same method can be used for updating and uninstalling the plugin.

## How to Use

TODO: Enable it in Configure -> Plugins then just connect to http://localhost:8086/websocket with your client and get the data pushed to you as event: data formatted JSON. Sending 'close' disconnects you. Will add more details and the exact APIs later in development.
