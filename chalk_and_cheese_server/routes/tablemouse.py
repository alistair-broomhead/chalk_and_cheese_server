from .base import Router


class TableMouse(Router):

    _sub = Router.Sub('/table/<table_id>/<mouse_id>')

    @_sub.get()
    def get(self, table_id, mouse_id):
        return self.views.tables[table_id].mouse_view(mouse_id).show

    @_sub.get('/updated')
    def updated(self, table_id, mouse_id):
        return self.views.tables[table_id].mouse_view(mouse_id).updated