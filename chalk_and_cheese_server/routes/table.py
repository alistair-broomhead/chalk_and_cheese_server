from .. import utils
from ..models.table import TableStates
from ..models.mouse import Mouse as MouseModel
from .base import Router


class Table(Router):

    _sub = Router.Sub('/table/<table_id>')

    @_sub.get()
    def get(self, table_id):
        return self.views.tables[table_id].show

    @_sub.get('/updated')
    def updated(self, table_id):
        return self.views.tables[table_id].updated

    @_sub.post('/token')
    def place(self, table_id):
        self.views.tables[table_id].place()

    @_sub.get('/token/<token_id>')
    def draw(self, table_id, token_id):
        self.views.tables[table_id].draw(model=MouseModel[token_id])

    @_sub.post('/bid')
    def bid(self, table_id):
        self.views.tables[table_id].place_bid()

    @_sub.delete('/bid')
    def stand(self, table_id):
        self.views.tables[table_id].stand()