from ..models.mouse import Mouse as MouseModel
from .base import Router


class Mouse(Router):

    _sub = Router.Sub('/mouse/<mouse_id>')

    @_sub.get()
    def display(self, mouse_id):
        return self.views.mice[mouse_id].show

    @_sub.get('/updated')
    def updated(self, mouse_id):
        return self.views.mice[mouse_id].updated