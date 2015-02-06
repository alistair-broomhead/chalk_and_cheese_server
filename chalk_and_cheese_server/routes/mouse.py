from ..models.mouse import Mouse as MouseModel
from .base import Router


class Mouse(Router):

    _sub = Router.Sub('/mouse/<mouse_id>')

    def __getitem__(self, item):
        return MouseModel.connected[int(item)]

    def __init__(self, app, views, lobby):
        super(Mouse, self).__init__(app, views)
        self.lobby = lobby

    @staticmethod
    def _mouse(mouse_id):
        return MouseModel.connected[int(mouse_id)]

    @_sub.get()
    def display(self, mouse_id):
        mouse = self[mouse_id]
        return {
            'uid': mouse.uid,
            'name': mouse.name
        }

    @_sub.get('/updated')
    def updated(self, mouse_id):
        ret = {
            'change': self[mouse_id].updated(self.user)
        }
        if ret['change']:
            ret['data'] = self.display()

        return ret