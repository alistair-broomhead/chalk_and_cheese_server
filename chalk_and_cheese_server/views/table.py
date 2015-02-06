from .base import ViewBase
from ..models.table import TableStates


class TablesView(object):
    """
    For pure convenience
    """
    def __init__(self, lobby_view):
        self.lobby = lobby_view
        self.models = {}

    def __getitem__(self, item):
        if item not in self.models:
            self.models[item] = TableView(self.lobby.model.games[item])

        return self.models[item]


class TableView(ViewBase):

    def _table_mouse(self, user, model, mouse):

        #TODO - Have actual TableMouse View

        d = self.views.mice[mouse].show

        if mouse is user:
            d['hand'] = model.hands[mouse]
            d['stack'] = model.stacks[mouse]
        else:
            d['hand'] = len(model.hands[mouse])
            d['stack'] = len(model.stacks[mouse])

        d['points'] = model.points[mouse]

        if model.state is TableStates.bidding:
            d['bid'] = model.bids[mouse]
        elif model.state is TableStates.raid and user is model.active_player:
            d['bid'] = model.bid_current
        else:
            d['bid'] = 0
        return d

    def show(self):
        user = self.user
        model = self.model

        ret = {
            'uid': model.uid,
            'mice': {
                mouse.uid: self._table_mouse(user, model, mouse)
                for mouse in model.mice
            },
            'state': model.state.name,
            'turn': model.active_player.uid
        }

        if model.state is TableStates.raid:
            ret['taken'] = [[m.uid, token] for m, token in model.raided]
        return ret

    def __init__(self, table_model, views):
        self.model = table_model
        self.views = views

    @property
    def bid(self):
        return self.model.bids[self.user]

