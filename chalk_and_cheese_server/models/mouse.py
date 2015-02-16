import random
import string

from .base import ModelBase


class MouseMeta(type):
    connected = {}

    def __getitem__(self, item):
        return self.connected[int(item)]


class Mouse(ModelBase):
    __metaclass__ = MouseMeta
    connected = {}

    def __init__(self, uid, name, password, tables):
        super(Mouse, self).__init__()
        self.uid = uid
        self.name = name
        self.password = password
        self.connected[uid] = self
        self._tables = tables

    @property
    def tables(self):
        return sorted(list(self._tables))

    @tables.setter
    def change(self, uid, name=None, password=None, **_):
        assert uid == self.uid
        changed = False
        if name is not None:
            self.name = name
            changed = True
        if password is not None:
            self.password = password
            changed = True

        if changed:
            self.update()

        return changed

    @classmethod
    def random_password(cls):
        return ''.join(random.choice(string.printable)
                       for _ in xrange(random.randint(8, 16)))

    @classmethod
    def new(cls, name=None, password=None):
        # Get the next user id
        uid = 0 if not cls.connected else max(cls.connected) + 1
        # Generate a random password
        if password is None:
            password = cls.random_password()
        # Create the user with these credentials
        if name is None:
            name = "mouse_{0}".format(uid)
        mouse = cls(uid, name, password, set())
        return mouse