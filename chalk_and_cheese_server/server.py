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

from .models.mouse import Mouse
from .models.lobby import Lobby
from .models.table import TableStates

APP = bottle.Bottle()


def add_endpoints(app=APP):

    from .utils import (body,
                        with_auth,
                        with_user_and_table,
                        with_update,
                        to_json)

    lobby = Lobby()

    with_user_and_table = with_user_and_table(lobby)
    with_update = with_update(lobby)

    # Player Endpoints

    @app.route('/', method='GET')
    def root():
        return "Hi"

    @app.route('/player', method='GET')
    @with_auth
    def get_mice(user):
        """
        Check current user info.
        """
        return user.to_dict(player=True)

    @app.route('/player', method='PUT')
    @with_auth
    def change_mouse(user):
        """
        Change user data such as name or password. (must have a session to edit)
        """
        if user.update(**body()):
            lobby.update()
            for table in user.games:
                table.update()
        return user.to_dict(player=True)

    @app.route('/player', method='POST')
    def create_mouse():
        """
        Join the session, get the auth data used for other requests. (must not
        have a current session)
        """
        user = Mouse.new()
        lobby.join(user)
        return user.to_dict(player=True)

    @app.route('/player/updated', method='GET')
    @with_auth
    @to_json
    def get_updated(user):
        """
        Is there anything new for the player to know?
        """
        #TODO - make this "Has the player model changed since last update"
        ret = {
            'change': user.wait_for_update()
        }
        if ret['change']:
            ret['data'] = user.to_dict(player=True)

        return ret
    
    @app.route('/table/<table_id>', method='GET')
    @with_auth
    def get_game(user, table_id):
        """ Get progress of current game """
        return lobby.games[int(table_id)].display_for(user)

    @app.route('/table/<table_id>/updated', method='GET')
    @with_auth
    @to_json
    def get_updated(user, table_id):
        """
        Is there anything new for the player to know?
        """
        table = lobby.games[int(table_id)]
        ret = {
            'change': table.wait_for_update(user)
        }
        if ret['change']:
            ret['data'] = table.display_for(user)
        return ret

    @app.route('/table/<table_id>/token', method='POST')
    @with_auth
    @with_update
    def place_token(user, table_id):
        """ Place either a chalk or a cheese.(must be your turn) """
        table = lobby.games[int(table_id)]
        assert table.state is TableStates.placement
        return table.place(user=user, card=bottle.request.body.read())

    @app.route('/table/<table_id>/token/<uid>', method='GET')
    @with_auth
    @with_update
    def draw_token(user, table_id, uid):
        """ Draw a token from the top of the given pile. (must be raiding) """
        table = lobby.games[int(table_id)]
        assert table.state is TableStates.raid
        return table.take(user=user, mouse=Mouse.connected[int(uid)])

    @app.route('/table', method='POST')
    @with_auth
    def new_game(user):
        """ Vote to start a new game. (there must not be one in progress) """
        lobby.add_vote(user)
        return json.dumps(user not in lobby.mice)

    @app.route('/table/<table_id>/bid', method='POST')
    @with_auth
    @with_update
    def post_bid(user, table_id):
        """ Place a bid (must be your turn) """
        table = lobby.games[int(table_id)]
        return table.bid(user=user, num=body())

    @app.route('/table/<table_id>/bid', method='DELETE')
    @with_auth
    @with_update
    def withdraw_bid(user, table_id):
        """ Place a bid (must be your turn) """
        table = lobby.games[int(table_id)]
        return table.stand(user=user)

    @app.route('/lobby', method='GET')
    @with_auth
    def get_mice(user):
        """
        What does this user know about their current room, whether this is the
        lobby or a table.
        """
        return lobby.display_for(user)

    @app.route('/lobby/ready', method='GET')
    @with_auth
    def get_ready(user):
        """ Is the user ready to play? """
        #TODO - change when I implement new lobby system
        return user in lobby.start_votes

    @app.route('/lobby/ready', method='POST')
    @with_auth
    def set_ready(user):
        """ Set whether the user is ready to play """
        #TODO - change when I implement new lobby system
        body = bottle.request.body.read()
        if body and json.loads(body):
            lobby.add_vote(user)
        else:
            lobby.remove_vote(user)

    @app.route('/lobby/updated', method='GET')
    @with_auth
    @to_json
    def get_updated(user):
        """
        Is there anything new for the player to know?
        """
        #TODO - make this "Has the player model changed since last update"
        ret = {
            'change': lobby.wait_for_update(user)
        }
        if ret['change']:
            ret['data'] = lobby.display_for(user)
        return ret

    @app.route('/mouse/hand', method='GET')
    @with_user_and_table
    def get_hand(user, table):
        """ Get the cards currently in your hand. (Game must be in progress) """
        return json.dumps(table.hands[user])

    @app.route('/mouse/chalk', method='GET')
    @with_user_and_table
    def get_chalk(user, table):
        """ Get the user's chalk image. (Game must be in progress) """
        assert table
        return 'chalk'  # TODO - use image

    @app.route('/mouse/cheese', method='GET')
    @with_user_and_table
    def get_cheese(user, table):
        """ Get the user's cheese image. (Game must be in progress) """
        assert table
        return 'cheese'  # TODO - use image

    def add_cross_origin_headers(response,
                                 origin=True, methods=True, auth=True):
        if origin:
            response.set_header('Access-Control-Allow-Origin', '*')
        if methods:
            response.set_header('Access-Control-Allow-Methods',
                                'GET, POST, PUT, DELETE')
        if auth:
            response.set_header('Access-Control-Allow-Headers',
                                'Authorization, Origin, '
                                'X-Requested-With, '
                                'Content-Type, '
                                'Accept')
        return response

    @app.error(405)
    @app.error(500)
    def method_not_allowed(res):
        if bottle.request.method == 'OPTIONS':
            return add_cross_origin_headers(bottle.HTTPResponse())
        res.headers['Allow'] += ', OPTIONS'
        return bottle.request.app.default_error_handler(res)

    @app.hook('after_request')
    def enable_cors():
        add_cross_origin_headers(bottle.response, methods=False)


def run(app=bottle):
    add_endpoints(app.route)
    app.run()