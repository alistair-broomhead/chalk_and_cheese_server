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
        return self.views.players.joined(new_model=Mouse)

    @_sub.delete()
    def leave(self):
        self.lobby.leave(self.user)

    @_sub.get('/updated')
    def updated(self):
        return self.views.players.updated