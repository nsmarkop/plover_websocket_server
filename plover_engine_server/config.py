"""Server configuration."""

import json


DEFAULT_HOST: str = 'localhost'
DEFAULT_PORT: int = 8086


class ServerConfig():
    """Loads server configuration.

    Attributes:
        host: The host address for the server to run on.
        port: The port for the server to run on.
    """

    host: str
    port: str

    def __init__(self, file_path: str):
        """Initialize the server configuration object.

        Args:
            file_path: The file path of the configuration file to load.

        Raises:
            IOError: Errored when loading the server configuration file.
        """

        try:
            with open(file_path, 'r', encoding='utf-8') as config_file:
                data: dict = json.load(config_file)
        except FileNotFoundError:
            data = {}

        self.host = data.get('host', DEFAULT_HOST)
        self.port = data.get('port', DEFAULT_PORT)
