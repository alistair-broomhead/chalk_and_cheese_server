from .base import ViewBase


class MouseView(ViewBase):
    @property
    def show(self):
        return {
            'uid': self.model.uid,
            'name': self.model.name,
        }

    @property
    def tables(self):
        return {
            table.uid: self.views.tables[table.uid][self.model]
            for table in self.model.tables
        }

    def __init__(self, views, mouse_model):
        self.views = views
        self.model = mouse_model


class MiceView(object):
    """
    For pure convenience
    """

    _view_class = MouseView

    def __init__(self, views):
        self.views = views
        self.mouse_views = {}

    @property
    def mice(self):
        return self.views.lobby.model.mice

    def from_uid(self, uid):
        return self[self.mice[uid]]

    def __getitem__(self, item):
        if item not in self.mouse_views:
            self.mouse_views[item] = self._view_class(self.views,
                                                      self.mice[item.uid])

        return self.mouse_views[item]