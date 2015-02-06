from .base import ViewBase


class MiceView(object):
    """
    For pure convenience
    """
    def __init__(self, lobby_view):
        self.lobby = lobby_view
        self.models = {}

    def from_uid(self, uid):
        return self[self.lobby.show[uid]]

    def __getitem__(self, item):
        if item not in self.models:
            self.models[item] = MouseView(self.lobby.model.mice[item])

        return self.models[item]


class MouseView(ViewBase):

    def show(self):
        return {
            'uid': self.model.uid,
            'name': self.model.name,
        }

    def __init__(self, mouse_model):
        self.model = mouse_model