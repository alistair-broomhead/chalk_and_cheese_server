from collections import deque
import random
from .base import ModelBase


class Table(ModelBase):
    next_id = 0

    def __init__(self, mice):
        super(Table, self).__init__()
        from .table_mouse import TableMouse
        self.uid, self.__class__.next_id = self.next_id, self.next_id + 1

        self.mice = {
            mouse.uid: TableMouse(self, mouse) for mouse in mice
        }
        self.order = deque(random.shuffle(self.mice.keys()))
        self.highest_bid = None

        self.version = 0
        self._seen = {}
        self.state = TableStates.placement
        self.bid_max = self.bid_current = None
        self.raided = []
        self.update()

    def __getitem__(self, item):
        return self.mice[item.uid]

    def return_stacks(self):
        for mouse in self.mice:
            mouse.return_stack()

    def __len__(self):
        return len(self.order)

    @property
    def turn(self):
        for key in self.order:
            yield self.mice[key]

    @property
    def current(self):
        """
        :rtype : TableMouse
        """
        return self.mice[self.order[0]]

    def assert_turn(self, user):
        assert user is self.current.mouse

    def next(self):
        self.order.rotate(-1)

        if self.state is TableStates.bidding and self.current is self.highest_bid:
            self.state = TableStates.raid
            self.raided = []

    def remove_mouse(self, mouse=None):
        mouse = self.current if mouse is None else mouse
        del self.mice[mouse.mouse.uid]
        self.order.remove(mouse)

    def place(self, user, card):
        """
        Places a card on the table from the mouse's hand
        """
        self.assert_turn(user)
        self.current.place(card)
        self.next()
        self.update()

    def bid(self, user, num):
        """
        Places a bid for the next raid
        """
        self.assert_turn(user)
        self.current.bid(num)
        self.highest_bid = self.current
        self.next()
        self.update()

    def stand(self, user):
        """
        Stand down from the next raid
        """
        self.assert_turn(user)
        self.current.stand()
        self.next()
        self.update()

    def take(self, user, mouse):
        """
        During a raid take a card from the given mouse
        """
        self.assert_turn(user)
        user = self.current
        user.take(self[mouse])

        if self.state is TableStates.placement:
            self.return_stacks()
            self.raided = []

            if not user.hand:
                self.remove_mouse(user)

        self.update()

    @property
    def active_player(self):
        return self.current.mouse


class TableStates(object):
    placement = object()
    bidding = object()
    raid = object()
    finished = object()