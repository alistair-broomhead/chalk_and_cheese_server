from .base import ViewBase


class LobbyMouseView(ViewBase):

    def __init__(self, views, mouse):
        self.views = views
        self.mouse = mouse

    def show(self):
        return {
            'uid': self.mouse.uid,
            'ready': self.lobby_model[self.mouse].ready
        }

    @property
    def lobby_model(self):
        return self.views.lobby.model

    @property
    def ready(self):
        return {
            'ready': self.lobby_model[self.mouse].ready
        }

    @ready.setter
    def ready(self, value):
        self.lobby_model[self.mouse].ready = value


class LobbyView(ViewBase):

    def __init__(self, views):
        self.views = views
        self.lobby_mice = {}

    def __getitem__(self, item):
        if item not in self.lobby_mice:
            self.lobby_mice[item] = LobbyMouseView(self.views, item)
        return self.lobby_mice[item]

    @property
    def show(self):
        view = {
            mouse.uid: self[mouse].ready
            for mouse in self.model.connected
        }
        return view

    @property
    def ready(self):
        return self[self.user].ready

    @ready.setter
    def ready(self, value):
        self[self.user].ready = value
