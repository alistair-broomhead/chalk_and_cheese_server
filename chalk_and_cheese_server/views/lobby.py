from .base import ViewBase


class LobbyView(ViewBase):

    @property
    def show(self):
        return {
            mouse.uid: mouse in self.model.start_votes
            for mouse in self.model.connected
        }

    @property
    def ready(self):
        return dict(ready=self.user in self.model.start_votes)

    @ready.setter
    def ready(self, value):
        if value:
            self.model.add_vote(self.user)
        else:
            self.model.remove_vote(self.user)
