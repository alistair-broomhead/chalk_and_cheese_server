from .base import ViewBase
from ..models.table import TableStates
from .table_mouse import TableMice
from .. import utils


class TablesView(object):
    """
    For pure convenience
    """

    def __init__(self, views):
        self.views = views
        self.table_views = {}

    @property
    def games(self):
        return self.views.lobby.model.games

    def __getitem__(self, item):
        item = int(item)
        if item not in self.table_views:
            self.table_views[item] = TableView(self.games[item], self.views)

        return self.table_views[item]


class TableView(ViewBase):
    def __init__(self, table_model, views):
        self.model = table_model
        self.views = views
        self.mouse_views = TableMice(self)

    def __getitem__(self, mouse_model):
        return self.mouse_views[mouse_model]

    @property
    def show(self):
        model = self.model

        ret = {
            'uid': model.uid,
            'mice': {mouse.uid: self[mouse].show for mouse in self.model.mice},
            'state': model.state.name,
            'turn': model.active_player.uid
        }

        if model.state is TableStates.raid:
            ret['taken'] = [[m.uid, token] for m, token in model.raided]
        return ret

    def place(self):
        self.model.place(user=self.user, card=utils.body())

    def draw(self, model):
        self.model.take(user=self.user, model=model)

    def place_bid(self):
        self.model.bid(user=self.user, num=utils.body())

    def stand(self):
        self.model.stand(user=self.user)

    @property
    def bid(self):
        return self.model.bids[self.user]