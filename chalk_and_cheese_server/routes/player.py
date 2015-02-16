from ..models.mouse import Mouse
from .. import utils
from .base import Router


class Player(Router):

    _sub = Router.Sub('/player')

    def __init__(self, app, views, lobby):
        super(Player, self).__init__(app, views)
        self.lobby = lobby

    @_sub.get()
    def display(self):
        return self.views.players[self.user].show

    @_sub.put()
    def change(self):
        self.user.change(**self.body)
        return self.views.players[self.user].show

    @_sub.post()
    def join(self):
        user_dict = utils.json_body(default={})
        user_view = self.views.players.from_uid_password(
            uid=user_dict.get('uid', None),
            password=user_dict.get('password', None)
        )

        if user_view is None:
            user = Mouse.new(name=user_dict.get('name', None),
                             password=user_dict.get('password', None))
            self.lobby.join(user)
            user_view = self.views.players[user]
        else:
            user = user_view.model
            self.lobby.join(user)

        return user_view.show

    @_sub.delete()
    def leave(self):
        self.lobby.leave(self.user)

    @_sub.get('/updated')
    def updated(self):
        #TODO - make this "Has the player model changed since last update"
        user = self.user
        ret = {
            'change': user.updated(user)
        }
        if ret['change']:
            ret['data'] = self.views.players[self.user].show

        return ret