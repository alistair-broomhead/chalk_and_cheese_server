"""
"""
import os

import bottle

from .views import Views
from .models.lobby import Lobby
from .routes import add_routes


def add_endpoints(app=bottle):

    lobby = Lobby()
    views = Views()

    add_routes(app=app, lobby_model=lobby, views=views)

    def add_cross_origin_headers(response,
                                 origin=True, methods=True, auth=True):
        if origin:
            response.set_header('Access-Control-Allow-Origin', '*')
        if methods:
            response.set_header('Access-Control-Allow-Methods',
                                'GET, POST, PUT, DELETE')
        if auth:
            response.set_header('Access-Control-Allow-Headers',
                                'Authorization, Origin, '
                                'X-Requested-With, '
                                'Content-Type, '
                                'Accept')
        return response

    @app.error(405)
    @app.error(500)
    def method_not_allowed(res):
        res = add_cross_origin_headers(bottle.HTTPResponse())
        if bottle.request.method == 'OPTIONS':
            return res
        res.headers['Allow'] += ', OPTIONS'
        return bottle.request.app.default_error_handler(res)

    @app.hook('after_request')
    def enable_cors():
        add_cross_origin_headers(bottle.response, methods=False)


def run(app=bottle):
    add_endpoints(bottle)

    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", '0.0.0.0')

    app.run(server='gevent', host=host, port=port, reloader=True)