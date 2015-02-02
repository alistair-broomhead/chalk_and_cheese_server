import random
import string
import time
import gevent
from .event import Event


class Mouse(object):
    connected = {}

    def __init__(self, uid, name, password, games):
        self.uid = uid
        self.updated = True
        self.name = name
        self.password = password
        self.connected[uid] = self
        self.games = games

    def wait_for_update(self,
                        time_out_in_seconds=10,
                        step_time_in_seconds=0.2):
        end_time = time.time() + time_out_in_seconds
        while time.time() < end_time:
            if self.updated:
                self.updated = False
                return True
            gevent.sleep(step_time_in_seconds)
        return False

    def update(self, uid, name=None, password=None, **_):
        assert uid == self.uid
        if name is not None:
            self.name = name
        if password is not None:
            self.password = password
        return not ((name is None) and
                    (password is None))

    @classmethod
    def random_password(cls):
        return ''.join(random.choice(string.printable)
                       for _ in xrange(random.randint(8, 16)))

    @classmethod
    def new(cls):
        # Get the next user id
        uid = 0 if not cls.connected else max(cls.connected) + 1
        # Generate a random password
        #TODO - have flag somewhere for password randomness
        password = cls.random_password()
        password = "password"
        # Create the user with these credentials
        mouse = cls(uid, "mouse_{0}".format(uid), password, set())
        Event("new mouse", mouse)
        return mouse

    def to_dict(self, player=False):
        ret = {
            'uid': self.uid,
            'name': self.name
        }
        if player:
            ret['password'] = self.password
            ret['tables'] = list(self.games)
        return ret