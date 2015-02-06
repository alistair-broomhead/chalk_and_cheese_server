from abc import ABCMeta
import gevent


class ModelBase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.version = 0
        self._seen = {}

    def update(self):
        """
        A method that marks the given model as updated for all relevant users
        """
        self.version += 1

    def updated(self, user):
        """
        A method that returns whether the given user's copy of this model
        needs to be updated.

        This method may wait until there is indeed something to show.
        """
        while self._seen.get(user.uid, -1) == self.version:
            gevent.sleep(0.1)
        self._seen[user.uid] = self.version
        return True