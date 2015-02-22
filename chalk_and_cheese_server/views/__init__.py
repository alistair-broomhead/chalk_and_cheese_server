from .lobby import LobbyView
from .table import TablesView
from .player import PlayersView
from .mouse import MiceView


class Views(object):
    def __init__(self):
        self.lobby = LobbyView()
        self.tables = TablesView(self)
        self.players = PlayersView(self)
        self.mice = MiceView(self)

    @staticmethod
    def bind(lobby_model):
        LobbyView.model = lobby_model