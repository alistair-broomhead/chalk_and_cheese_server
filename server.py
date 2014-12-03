"""
/table          POST    Vote to start a new game. (there must not be one in
                        progress)

/mouse          GET     Get a list of connected users.
/mouse          PUT     Change user data such as name or password. (must have a
                        session to edit)
/mouse          POST    Join the session, get the auth data used for other
                        requests. (must not have a current session)

/mouse/hand     GET     Get the cards currently in your hand. (Game must be in
                        progress)
/mouse/chalk    GET     Get the user's chalk image. (Game must be in progress)
/mouse/cheese   GET     Get the user's cheese image. (Game must be in progress)

/token          POST    Place either a chalk or a cheese.(must be your turn)
/token/{pile}   GET     Draw a token from the top of the given pile. (must be
                        raiding)

/bid            POST    Place a bid (must be your turn)
/bid            DELETE  Withdraw from bidding (must be your turn)
"""
import json
import bottle
from functools import wraps
from models import Mouse, Lobby, TableStates
LOBBY = Lobby()


def body():
    return json.load(bottle.request.body)


def _auth_user():
    user_id, password = bottle.request.auth
    user = Mouse.connected[json.loads(user_id)]
    assert user.password == password
    return user


def with_auth(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        kwargs['user'] = _auth_user()
        return fn(*args, **kwargs)
    return inner


def with_user_and_table(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        kwargs['user'] = user = _auth_user()
        kwargs['table'] = LOBBY.tables[user]
        return fn(*args, **kwargs)
    return inner


def add_endpoints(app):

    @app.post('/table')
    @with_auth
    def new_game(user):
        """ Vote to start a new game. (there must not be one in progress) """
        LOBBY.add_vote(user)
        return get_mice()

    @app.get('/mouse')
    @with_auth
    def get_mice(user):
        """
        What does this user know about their current room, whether this is the
        lobby or a table.
        """
        if user in LOBBY.mice:
            return LOBBY.display_for(user)
        else:
            return LOBBY.tables[user].display_for(user)

    @app.put('/mouse')
    @with_auth
    def change_mouse(user):
        """
        Change user data such as name or password. (must have a session to edit)
        """
        _body = body()
        assert user.uid == _body['uid']
        if 'name' in _body:
            user.name = _body['name']
        if 'password' in _body:
            user.password = _body['password']
        return user.to_dict(password=True)

    @app.post('/mouse')
    def create_mouse():
        """
        Join the session, get the auth data used for other requests. (must not
        have a current session)
        """
        mouse = Mouse.new()
        LOBBY.mice.add(mouse)
        return mouse.to_dict(password=True)

    @app.get('/mouse/hand')
    @with_user_and_table
    def get_hand(user, table):
        """ Get the cards currently in your hand. (Game must be in progress) """
        return json.dumps(table.hands[user])

    @app.get('/mouse/chalk')
    @with_user_and_table
    def get_chalk(user, table):
        """ Get the user's chalk image. (Game must be in progress) """
        assert table
        return 'chalk'  # TODO - use image

    @app.get('/mouse/cheese')
    @with_user_and_table
    def get_cheese(user, table):
        """ Get the user's cheese image. (Game must be in progress) """
        assert table
        return 'cheese'  # TODO - use image

    @app.post('/token')
    @with_user_and_table
    def place_token(user, table):
        """ Place either a chalk or a cheese.(must be your turn) """
        _body = body()
        return table.place(user=user, card=_body)

    @app.get('/token/<uid>')
    @with_user_and_table
    def draw_token(user, table, uid):
        """ Draw a token from the top of the given pile. (must be raiding) """
        assert table.state is TableStates.raid
        return table.take(user=user, mouse=Mouse.connected[int(uid)])

    @app.post('/bid')
    @with_user_and_table
    def post_bid(user, table):
        """ Place a bid (must be your turn) """
        return table.bid(user=user, num=body())

    @app.delete('/bid')
    @with_user_and_table
    def withdraw_bid(user, table):
        """ Place a bid (must be your turn) """
        return table.stand(user=user)


def run(app=bottle):
    add_endpoints(app)
    app.run()