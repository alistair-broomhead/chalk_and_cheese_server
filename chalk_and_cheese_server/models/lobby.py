from .base import ModelBase
from .table import Table


class Lobby(ModelBase):
    games = {}

    def __init__(self):
        super(Lobby, self).__init__()
        self._connected = {}
        self.mice = {}
        self.start_votes = set()

    @property
    def connected(self):
        return set(mouse for mouse, conn in self._connected.items() if conn)

    def join(self, mouse):
        self._connected[mouse] = True
        self.mice[mouse.uid] = mouse
        self.update()

    def leave(self, mouse):
        self._connected[mouse] = False
        self.update()

    def add_vote(self, mouse):
        if mouse in self._connected:
            self.start_votes.add(mouse)
            self.update()

            if len(self.start_votes) > 1:
                self.start()

    def remove_vote(self, mouse):
        if mouse in self.start_votes:
            self.start_votes.remove(mouse)
            self.update()

    def start(self):

        self.start_votes, start_votes = set(), self.start_votes

        table = Table(start_votes)
        self.games[table.uid] = table
        for mouse in start_votes:
            mouse.tables.add(table.uid)

    def update(self):
        super(Lobby, self).update()
        for mouse in self._connected:
            mouse.update()