import json
import bottle
from .models.mouse import Mouse


def json_body(default=None):
    try:
        return json.load(bottle.request.body)
    except ValueError:
        if default is not None:
            return default
        raise


def body():
    return bottle.request.body.read()


def auth_user():
    auth = bottle.request.auth
    if auth is None:
        raise bottle.HTTPError(401)
    user_id, password = auth
    user_id = json.loads(user_id)
    if user_id not in Mouse.connected:
        raise bottle.HTTPError(401)
    user = Mouse.connected[user_id]
    if user.password != password:
        raise bottle.HTTPError(401)
    return user