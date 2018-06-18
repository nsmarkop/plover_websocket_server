from aiohttp import web
from plover_websocket_server.views import index, websocket_handler


def setup_routes(app: web.Application):
    '''
    Sets up the routes for the web server.

    :param app: The web server.
    '''

    app.router.add_get('/', index)
    app.router.add_get('/websocket', websocket_handler)
