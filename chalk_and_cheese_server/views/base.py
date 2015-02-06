from abc import ABCMeta, abstractproperty
from .. import utils


class ViewBase(object):
    __metaclass__ = ABCMeta

    model = None

    @abstractproperty
    def show(self):
        return {}

    @property
    def user(self):
        return utils.auth_user()