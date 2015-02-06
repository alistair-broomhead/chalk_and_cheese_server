from .. import utils
from .base import Router


class Lobby(Router):

    _sub = Router.Sub('/lobby')

    @_sub.get()
    def get(self):
        return self.views.lobby.show

    @_sub.post('/ready')
    def ready(self):
        self.views.lobby.ready = utils.json_body(default=False)
        return self.views.lobby.ready

    @_sub.get('/updated')
    def updated(self):
        return self.views.lobby.updated