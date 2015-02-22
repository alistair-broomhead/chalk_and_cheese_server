from collections import deque
import random
import time
import gevent
from functools import wraps
from .base import ModelBase


def in_turn(action):
    @wraps(action)
    def inner(self, user, *args, **kwargs):
        kwargs['user'] = user
        assert user is self.active_player
        assert action.__name__ in (a.__name__ for a in self.state.actions)
        return action(self, *args, **kwargs)
    return inner


class Table(ModelBase):
    next_id = 0

    def __init__(self, mice):
        super(Table, self).__init__()
        self.uid, self.__class__.next_id = self.next_id, self.next_id + 1
        self.mice = deque(sorted(list(mice)))

        self.version = 0
        self._seen = {}

        self.updates = {mouse: False for mouse in self.mice}
        self.hands = {mouse: ['chalk', 'cheese', 'cheese', 'cheese']
                      for mouse in mice}
        self.stacks = {mouse: [] for mouse in mice}
        self.points = {mouse: 0 for mouse in mice}
        # Choose a random starting mouse
        self.mice.rotate(random.randint(1, len(self.mice)))
        self.state = TableStates.placement
        self.bids = {}
        self.bid_max = self.bid_current = None
        self.raided = []
        self.update()

    def wait_for_update(self,
                        mouse,
                        time_out_in_seconds=10,
                        step_time_in_seconds=0.2):
        if not mouse in self.mice:
            return False
        end_time = time.time() + time_out_in_seconds
        while time.time() < end_time:
            if self.updates[mouse]:
                self.updates[mouse] = False
                return True
            gevent.sleep(step_time_in_seconds)
        return False

    @property
    def active_player(self):
        return self.mice[0]

    def _to_raid_state(self, user):
        assert self.state is TableStates.bidding
        while self.active_player is not user:
            self.mice.rotate(-1)
        self.state = TableStates.raid
        self.raided = []

    def _rotate_bids(self):
        """
        Rotate through the mice who are bidding - go to raid if there's only one
        """
        assert self.state is TableStates.bidding
        self.mice.rotate(-1)                        # Next player's turn!
        while self.active_player not in self.bids:  # But only if still bidding
            self.mice.rotate(-1)

        if len(self.bids) == 1:                     # Only one remaining bidder?
            self._to_raid_state(self.active_player)  # Then it's raid time!

    def _return_stacks(self):
        for other_mouse in self.mice:
            self.hands[other_mouse].extend(self.stacks[other_mouse])
            self.stacks[other_mouse] = []

    @in_turn
    def place(self, user, card):
        """
        Places a card on the table from the mouse's hand
        """
        assert card in self.hands[user]
        self.hands[user].remove(card)
        self.stacks[user].append(card)
        self.mice.rotate(-1)
        self.update()

    @in_turn
    def bid(self, user, num):
        """
        Places a bid for the next raid
        """
        assert user is self.active_player
        if self.state is TableStates.placement:
            self.bid_current = 0
            self.bid_max = sum(len(stack) for stack in self.stacks.values())
            # Are we allowed to enter bidding yet?
            assert self.bid_max >= len(self.mice)
            self.bids = {mouse: 0 for mouse in self.mice}
            self.state = TableStates.bidding
        assert self.state is TableStates.bidding
        assert user in self.bids
        assert self.bid_current < num <= self.bid_max

        self.bid_current = self.bids[user] = num

        if num == self.bid_max:
            # If it's impossible to bid higher, you've won the bid
            self._to_raid_state(user)
        else:
            self._rotate_bids()
        self.update()

    @in_turn
    def stand(self, user):
        """
        Stand down from the next raid
        """
        b = self.bids
        assert user in b
        del b[user]
        self._rotate_bids()
        self.update()

    @in_turn
    def take(self, user, mouse):
        """
        During a raid take a card from the given mouse
        """
        assert self.stacks[mouse]  # Is there a token on the stack?
        token = self.stacks[mouse].pop()
        self.hands[mouse].append(token)
        self.raided.append((mouse, token))

        if token == 'chalk':
            self._return_stacks()
            discard = random.choice(self.hands[user])
            self.hands[user].remove(discard)
            if not self.hands[user]:
                self.mice.remove(user)
            self.state = TableStates.placement
        elif len(self.raided) >= self.bid_current:
            self.points[user] += 1
            if self.points[user] == 2:
                self.state = TableStates.finished
            else:
                self._return_stacks()
                self.state = TableStates.placement

        self.update()


class TableState(object):
    def __init__(self, name, *actions):
        self.name = name
        self.actions = actions


class TableStates(object):
    placement = TableState('placement', Table.place, Table.bid)
    bidding = TableState('bidding', Table.bid, Table.stand)
    raid = TableState('raid', Table.take)
    finished = TableState('finished')