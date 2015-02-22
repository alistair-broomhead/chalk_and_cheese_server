from .mouse import MiceView, MouseView
from .. import utils
import sys


class PlayerView(MouseView):

    def leave(self):
        self.views.lobby.model.leave(self.user.model)

    @property
    def show(self):
        return {
            'uid': self.model.uid,
            'name': self.model.name,

            'password': self.model.password,
            'tables': self.model.tables,
        }


class PlayersView(MiceView):
    """
    For pure convenience
    """
    _view_class = PlayerView

    def joined(self, new_model):
        user_dict = utils.json_body(default={})

        try:
            mouse = self.mice[user_dict['uid']]
            assert mouse.password == user_dict['password'], \
                'Invalid credentials for {0}'.format(mouse)
        except KeyError as ex:
            print >> sys.stderr, 'Invalid:', ex
            user = self.new(user_dict=user_dict, model=new_model)
        except AssertionError as ex:
            print >> sys.stderr, ex
            user = self.new(user_dict=user_dict, model=new_model)
        else:
            user = self[mouse]
            self.views.lobby.model.join(user.model)

        return user.show

    def new(self, model, user_dict):
            user = model.new(name=user_dict.get('name', None),
                             password=user_dict.get('password', None))
            self.views.lobby.model.join(user)
            return self[user]

    def from_uid_password(self, uid=None, password=None):
        if uid is None or password is None:
            return
        mice = self.mice
        if uid in mice:
            mouse = mice[uid]
            if mouse.password == password:
                return self[mouse]