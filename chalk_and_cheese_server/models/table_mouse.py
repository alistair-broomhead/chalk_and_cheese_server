from collections import deque
import random
import bottle
from .base import ModelBase
from .table import Table, TableStates
from .mouse import Mouse


class TableMouse(ModelBase):
    def __init__(self, table, mouse):
        """
        :type table: Table
        :type mouse: Mouse
        """
        super(TableMouse, self).__init__()

        self.table = table
        self.mouse = mouse

        self.hand = ['chalk', 'cheese', 'cheese', 'cheese']
        self.stack = []
        self.bid = None
        self.points = 0

    @property
    def is_user(self):
        return self.mouse is self.user

    def return_stack(self):
        self.hand.extend(self.stack)
        self.stack = []
        self.update()

    def place(self, card):
        assert self.table.state is TableStates.placement
        assert card in self.hand
        self.hand.remove(card)
        self.stack.append(card)
        self.update()

    def bid(self, num):
        assert self.mouse is self.table.active_player
        if self.table.state is TableStates.placement:
            assert self.stack
            current = 0
            self.table.bid_max = sum(len(mouse.stack) for mouse in self.table)
            self.table.state = TableStates.bidding
        else:
            current = self.table.highest_bid.bid

        assert self.table.state is TableStates.bidding
        assert current < num <= self.table.bid_max
        self.update()

    def stand(self):
        self.bid = None
        self.update()

    def take(self, other):
        assert self.table.state is TableStates.raid
        assert other.stack

        if self.stack and self is not other:
            raise bottle.HTTPError(403)

        token = other.stack.pop()
        other.hand.append(token)
        self.table.raided.append(token)

        if token == 'chalk':
            self.table.return_stacks()
            self.hand.remove(random.choice(self.hand))
            self.table.state = TableStates.placement
        elif len(self.table.raided) >= self.bid:
            self.points += 1
            if self.points >= 2:
                self.table.state = TableStates.finished
            else:
                self.table.state = TableStates.placement
        self.update()