from functools import wraps
import json
import bottle
from .models.mouse import Mouse


def body():
    return json.load(bottle.request.body)


def _auth_user():
    user_id, password = bottle.request.auth
    user_id = json.loads(user_id)
    if user_id not in Mouse.connected:
        raise bottle.HTTPError(401)
    user = Mouse.connected[user_id]
    if user.password != password:
        raise bottle.HTTPError(401)
    return user


def with_auth(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        kwargs['user'] = _auth_user()
        return fn(*args, **kwargs)
    return inner


def with_update(lobby):
    def decorator(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            ret = fn(*args, **kwargs)
            kwargs['user'].update()
            lobby.update()
            return ret
        return inner
    return decorator


def with_user_and_table(lobby):
    def decorator(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            kwargs['user'] = user = _auth_user()
            kwargs['table'] = lobby.tables[user.uid]
            return fn(*args, **kwargs)
        return inner
    return decorator


def to_json(fn):
    @wraps(fn)
    def _inner(*args, **kwargs):
        ret = json.dumps(fn(*args, **kwargs))
        bottle.response.set_header('Content-Type', 'application/json')
        bottle.response.set_header('Content-Length', len(ret))
        return ret
    return _inner