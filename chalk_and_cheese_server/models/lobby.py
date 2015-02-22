from .base import ModelBase
from .table import Table


class LobbyMouse(object):
    def __init__(self, mouse, lobby):
        """
        :type mouse: Mouse
        :type lobby: Lobby
        """
        self.mouse = mouse
        self.lobby = lobby

    @property
    def ready(self):
        return self.mouse in self.lobby.start_votes

    @ready.setter
    def ready(self, value):
        if value:
            self.lobby.add_vote(self.mouse)
        else:
            self.lobby.remove_vote(self.mouse)


class Lobby(ModelBase):
    games = {}

    def __init__(self):
        super(Lobby, self).__init__()
        self._connected = {}
        self.mice = {}
        self.lobby_mice = {}
        self.start_votes = set()

    def __getitem__(self, item):
        if item not in self.lobby_mice:
            self.lobby_mice[item] = LobbyMouse(item, self)
        return self.lobby_mice[item]

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