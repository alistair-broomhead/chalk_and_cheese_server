from .. import utils
from ..models.table import TableStates
from ..models.mouse import Mouse as MouseModel
from .base import Router


class Table(Router):

    _sub = Router.Sub('/table/<table_id>')

    def __getitem__(self, item):
        table_id = int(item)
        return self.views.lobby.model.games[table_id]

    @_sub.get()
    def get(self, table_id):
        table_view = self[table_id]
        return table_view.show

    @_sub.get('/updated')
    def updated(self, table_id):
        table_view = self[table_id]
        ret = {
            'change': table_view.model.updated(self.user)
        }
        if ret['change']:
            ret['data'] = table_view.show
        return ret

    @_sub.post('/token')
    def place(self, table_id):
        table_view = self[table_id]
        assert table_view.model.state is TableStates.placement
        table_view.place(user=self.user, card=utils.body())
        return table_view.show

    @_sub.get('/token/<token_id>')
    def draw(self, table_id, token_id):
        table_view = self[table_id]
        assert self[table_id].state is TableStates.raid
        self[table_id].take(user=self.user,
                            mouse=MouseModel.connected[int(token_id)])
        return table_view.show

    @_sub.post('/bid')
    def bid(self, table_id):
        table_view = self[table_id]
        self[table_id].bid(user=self.user, num=self.body)
        return table_view.show

    @_sub.delete('/bid')
    def stand(self, table_id):
        table_view = self[table_id]
        self[table_id].stand(user=self.user)
        return table_view.show