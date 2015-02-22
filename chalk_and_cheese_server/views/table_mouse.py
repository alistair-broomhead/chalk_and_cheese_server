from .base import ViewBase
from .table import TableStates
from ..models.table_mouse import TableMouse as TableMouseModel


class TableMice(object):
    def __init__(self, table_view):
        self.table = table_view.model
        self.table_mice = {}

    def __getitem__(self, mouse_model):
        if mouse_model not in self.table_mice:
            self.table_mice[mouse_model] = TableMouse(mouse_model, self.table)
        return self.table_mice[mouse_model]


class TableMouse(ViewBase):

    def __init__(self, mouse_model, table_model):
        table_mouse_model = table_model[mouse_model]
        assert isinstance(table_mouse_model, TableMouseModel)
        self.model = table_mouse_model

    @property
    def uid(self):
        return self.model.mouse.uid

    @property
    def bid(self):
        if self.model.table.state is TableStates.placement:
            return None
        if self.model.table.state is TableStates.bidding:
            return self.model.bid
        if self.model.mouse is self.model.table.active_player:
            return self.model.bid
        return None

    @property
    def show(self):

        transform = (lambda x: x) if self.model.is_user else len

        view = {
            'uid': self.model.mouse.uid,
            'name': self.model.mouse.name,

            'hand': transform(self.model.hand),
            'stack': transform(self.model.stack),

            'points': self.model.points
        }

        bid = self.bid

        if bid is not None:
            view['bid'] = bid

        return view