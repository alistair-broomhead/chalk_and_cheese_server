from .player import Player
from .mouse import Mouse
from .table import Table
from .lobby import Lobby


def add_routes(app, lobby_model, views):

    views.bind(lobby_model)

    @app.route('/', method='GET')
    def root():
        return {
            'alive': True
        }

    Player(app, views, lobby_model).bind()
    Mouse(app, views).bind()
    Table(app, views).bind()
    Lobby(app, views).bind()