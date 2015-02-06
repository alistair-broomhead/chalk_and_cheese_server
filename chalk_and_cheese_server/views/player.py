from .base import ViewBase


class PlayersView(object):
    """
    For pure convenience
    """
    def __init__(self, lobby_view):
        self.lobby = lobby_view
        self.models = {}

    def from_uid_password(self, uid=None, password=None):
        if uid is None or password is None:
            return
        mice = self.lobby.show
        if uid in mice:
            mouse = mice[uid]
            if mouse.password == password:
                return self[mouse]

    def __getitem__(self, item):
        if item not in self.models:
            self.models[item] = PlayerView(self.lobby.model.mice[item])

        return self.models[item]


class PlayerView(ViewBase):

    def show(self):
        return {
            'uid': self.model.uid,
            'name': self.model.name,

            'password': self.model.password,
            'tables': self.model.tables,
        }

    def __init__(self, player_model):
        self.model = player_model