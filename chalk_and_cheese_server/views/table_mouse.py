from .base import ViewBase
from .table import TableStates


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
        self.uid = mouse_model.uid
        self.mouse_model = mouse_model
        self.table_model = table_model

    @property
    def show(self):

        table = self.table_model
        mouse = self.mouse_model

        hand = table.hands[mouse]
        stack = table.stacks[mouse]

        if mouse is not self.user:
            hand = len(hand)
            stack = len(stack)

        if table.state is TableStates.bidding:
            bid = table.points[mouse]
        elif table.state is TableStates.raid and mouse is table.active_player:
            bid = table.bid_current
        else:
            bid = 0

        return {
            'uid': mouse.uid,
            'name': mouse.name,

            'hand': hand,
            'stack': stack,
            'bid': bid,
            'points': table.points[mouse]
        }