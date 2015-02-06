from .lobby import LobbyView
from .table import TablesView
from .player import PlayersView
from .mouse import MiceView


class Views(object):
    def __init__(self):
        self.lobby = LobbyView()
        self.tables = TablesView(self.lobby)
        self.players = PlayersView(self.lobby)
        self.mice = MiceView(self.lobby)

    @staticmethod
    def bind(lobby_model):
        LobbyView.model = lobby_model