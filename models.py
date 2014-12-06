from collections import deque
import random
import string
from functools import wraps


class Event(object):

    audit = []

    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data
        self.audit.append(self)

    def __str__(self):
        return 'Event({0}, {1})'.format(
            self.event_type, self.data
        )


class Mouse(object):
    connected = {}

    def __init__(self, uid, name, password):
        self.uid = uid
        self.name = name
        self.password = password
        self.connected[uid] = self

    @classmethod
    def random_password(cls):
        return ''.join(random.choice(string.printable)
                       for _ in xrange(random.randint(8, 16)))
    @classmethod
    def new(cls):
        # Get the next user id
        uid = 0 if not cls.connected else max(cls.connected) + 1
        # Generate a random password
        password = cls.random_password()
        password = "password"
        # Create the user with these credentials
        mouse = cls(uid, "mouse_{0}".format(uid), password)
        Event("new mouse", mouse)
        return mouse

    def to_dict(self, uid=True, name=True, password=False):
        ret = {}
        if uid:
            ret['uid'] = self.uid
        if name:
            ret['name'] = self.name
        if password:
            ret['password'] = self.password
        return ret


class Lobby(object):
    tables = {}

    def __init__(self):
        self.mice = set()
        self.start_votes = set()

    def display_for(self, user):
        ret = {
            mouse.uid: mouse.to_dict(password=(mouse is user))
            for mouse in self.mice
        }
        ret['state'] = 'lobby'
        for mouse in self.mice:
            ret[mouse.uid]['ready'] = mouse in self.start_votes

        return ret

    def join(self, mouse):
        self.mice.add(mouse)
        Event("Mouse joined", {'mouse': mouse, 'lobby': self})

    def leave(self, mouse):
        self.mice.remove(mouse)
        Event("Mouse left", {'mouse': mouse, 'lobby': self})

    def add_vote(self, mouse):
        assert mouse not in self.tables
        if mouse in self.mice:
            self.start_votes.add(mouse)
            votes = len(self.start_votes)
            mice = len(self.mice)
            if votes > mice/2:
                self.start()

    def remove_vote(self, mouse):
        if mouse in self.start_votes:
            self.start_votes.remove(mouse)

    def start(self):
        mice, self.mice = self.mice, set()

        table = Table(mice)
        for mouse in mice:
            self.tables[mouse] = table


def in_turn(action):
    @wraps(action)
    def inner(self, user, *args, **kwargs):
        kwargs['user'] = user
        assert user is self.active_player
        assert action.__name__ in (a.__name__ for a in self.state.actions)
        return action(self, *args, **kwargs)
    return inner


class Table(object):
    connected = []

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
        return self.display_for(user)

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
            assert self.bid_max >= (2*len(self.mice)) - 1
            self.bids = {mouse: 0 for mouse in self.mice}
            self.state = TableStates.bidding
        assert self.state is TableStates.bidding
        assert user in self.bids
        assert self.bid_current < num <= self.bid_max

        self.bid_current = self.bids[user] = num

        if num == self.bid_max:
            # If it's impossible to bid higher, you've won the bid
            self.state = TableStates.raid
        else:
            self._rotate_bids()
        return self.display_for(user)

    @in_turn
    def stand(self, user):
        """
        Stand down from the next raid
        """
        b = self.bids
        assert user in b
        del b[user]
        self._rotate_bids()
        return self.display_for(user)

    @in_turn
    def take(self, user, mouse):
        """
        During a raid take a card from the given mouse
        """
        assert self.stacks[mouse]  # Is there a token on the stack?
        token = self.stacks[mouse].pop()
        self.hands[mouse].append(token)
        self.raided.append((mouse, token))

        display = self.display_for(user)

        if token == 'chalk':
            self._return_stacks()
            discard = random.choice(self.hands[user])
            self.hands[user].remove(discard)
            if not self.hands[user]:
                self.mice.remove(user)
            self.state = TableStates.placement
            return display
        elif len(self.raided) >= self.bid_current:
            self.points[user] += 1
            if self.points[user] == 2:
                self.state = TableStates.finished
                return display
            else:
                self._return_stacks()
                self.state = TableStates.placement

        return self.display_for(user)

    def display_for(self, user):
        ret = {
            'mice': {
                mouse.uid: mouse.to_dict(password=(mouse is user))
                for mouse in self.mice
            },
            'state': self.state.name,
            'turn': self.active_player.uid
        }
        for mouse in self.mice:
            d = ret['mice'][mouse.uid]
            d['points'] = self.points[mouse]
            if mouse is user:
                d['hand'] = self.hands[mouse]
                d['stack'] = self.stacks[mouse]
            else:
                d['hand'] = len(self.hands[mouse])
                d['stack'] = len(self.stacks[mouse])

        if self.state is TableStates.bidding:
            for mouse in self.bids:
                ret['mice'][mouse.uid]['bid'] = self.bids[mouse]
        elif self.state is TableStates.raid:
            ret['mice'][self.active_player.uid]['bid'] = self.bid_current
            ret['taken'] = [[m.uid, token] for m, token in self.raided]
        return ret

    def __init__(self, mice):
        self.uid = 0 if not self.connected else max(self.connected) + 1
        self.mice = deque(sorted(list(mice)))
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
        Event("New game", self)


class TableState(object):
    def __init__(self, name, *actions):
        self.name = name
        self.actions = actions


class TableStates(object):
    placement = TableState('placement', Table.place, Table.bid)
    bidding = TableState('bidding', Table.bid, Table.stand)
    raid = TableState('raid', Table.take)
    finished = TableState('finished')