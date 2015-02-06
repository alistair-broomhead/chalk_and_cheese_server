from abc import ABCMeta

from .. import utils
from functools import wraps


class Router(object):
    __metaclass__ = ABCMeta

    class Sub(object):
        def __init__(self, stem):
            self.stem = stem
            self.routes = []

        def __call__(self, url='', method='GET'):
            url = self.stem + url

            def decorator(fn):
                self.routes.append((fn, url, method))
                return fn
            return decorator

        def get(self, url=''):
            return self(url, 'GET')

        def put(self, url=''):
            return self(url, 'PUT')

        def post(self, url=''):
            return self(url, 'POST')

        def delete(self, url=''):
            return self(url, 'DELETE')

        def patch(self, url=''):
            return self(url, 'PATCH')

        def _bind(self, app, router, fn, url, method):
            code = fn.func_code
            binding = '{method} {url} {fn} {file}:{line}'.format(
                url=(url + ' ' * 30)[:30],
                method=(method + ' ' * 6)[:6],
                fn=(code.co_name + ' ' * 10)[:10],
                file=code.co_filename[53:],
                line=code.co_firstlineno
            )

            @wraps(fn)
            def _inner(*args, **kwargs):
                print binding
                return fn(router, *args, **kwargs)

            app.route(url, method=method)(_inner)

        def bind(self, router, app):
            for route in self.routes:
                self._bind(app, router, *route)

    _sub = Sub('')

    @property
    def user(self):
        return utils.auth_user()

    @property
    def body(self):
        return utils.json_body()

    def __init__(self, app, views):
        self.app = app
        self.views = views

    def bind(self):
        self._sub.bind(self, self.app)