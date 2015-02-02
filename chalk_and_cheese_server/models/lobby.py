import time
import gevent
from .table import Table
from .event import Event


class Lobby(object):
    tables = {}
    games = {}

    def __init__(self):
        self.mice = {}
        self.start_votes = set()

    def wait_for_update(self,
                        mouse,
                        time_out_in_seconds=10,
                        step_time_in_seconds=0.2):
        if not mouse in self.mice:
            return False
        end_time = time.time() + time_out_in_seconds
        while time.time() < end_time:
            if self.mice[mouse]:
                self.mice[mouse] = False
                return True
            gevent.sleep(step_time_in_seconds)
        return False

    def update(self):
        for mouse in self.mice:
            mouse.updated = True
            self.mice[mouse] = True

    def display_for(self, user):
        ret = {
            mouse.uid: mouse.to_dict(player=(mouse is user))
            for mouse in self.mice
        }
        for mouse in self.mice:
            ret[mouse.uid]['ready'] = mouse in self.start_votes

        return ret

    def join(self, mouse):
        self.mice[mouse] = True
        Event("Mouse joined", {'mouse': mouse, 'lobby': self})
        self.update()

    def leave(self, mouse):
        del self.mice[mouse]
        Event("Mouse left", {'mouse': mouse, 'lobby': self})
        self.update()

    def add_vote(self, mouse):
        assert mouse not in self.tables
        if mouse in self.mice:
            self.start_votes.add(mouse)
            if len(self.start_votes) > 1:
                self.start()
        self.update()

    def remove_vote(self, mouse):
        if mouse in self.start_votes:
            self.start_votes.remove(mouse)
        self.update()

    def start(self):

        self.start_votes, start_votes = set(), self.start_votes

        table = Table(start_votes)
        self.games[table.uid] = table
        for mouse in start_votes:
            mouse.games.add(table.uid)
            self.tables[mouse.uid] = table