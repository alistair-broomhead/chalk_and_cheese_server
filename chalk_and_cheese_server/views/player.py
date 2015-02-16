from .base import ViewBase
from .. import utils


class PlayersView(object):
    """
    For pure convenience
    """
    def __init__(self, lobby_view):
        self.lobby = lobby_view
        self.models = {}

    def joined(self, new_model):
        user = self.user

        if hasattr(user, 'model'):
            self.lobby.model.join(user.model)
        else:
            user = self.new(user_dict=user, model=new_model)

        return user.show

    @property
    def user(self):
        user_dict = utils.json_body(default={})
        user_view = self.from_uid_password(
            uid=user_dict.get('uid', None),
            password=user_dict.get('password', None)
        )
        return user_dict if user_view is None else user_view

    def new(self, model, user_dict):
            user = model.new(name=user_dict.get('name', None),
                             password=user_dict.get('password', None))
            self.lobby.model.join(user)
            return self[user]

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
            self.models[item] = PlayerView(self.lobby.model.mice[item.uid])

        return self.models[item]


class PlayerView(ViewBase):

    @property
    def show(self):
        return {
            'uid': self.model.uid,
            'name': self.model.name,

            'password': self.model.password,
            'tables': self.model.tables,
        }

    def __init__(self, player_model):
        self.model = player_model