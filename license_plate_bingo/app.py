import flask
import license_plate_bingo.db
import os
import uuid
import waitress
import werkzeug.middleware.proxy_fix

__version__ = '2022.0'

app = flask.Flask(__name__)
app.wsgi_app = werkzeug.middleware.proxy_fix.ProxyFix(app.wsgi_app, x_port=1)


def get_db() -> license_plate_bingo.db.Database:
    return license_plate_bingo.db.Database(os.getenv('DB'))


@app.before_request
def before_request():
    app.logger.debug(f'{flask.request.method} {flask.request.path}')
    # flask.session.permanent = True
    flask.g.version = __version__
    flask.g.debug_layout = True


@app.get('/')
def index():
    return flask.render_template('index.html')


@app.post('/update')
def update():
    for k, v in flask.request.values.lists():
        app.logger.debug(f'{k}: {v}')
    game_id = flask.request.values.get('game-id')
    db = get_db()
    game = db.games_get(game_id)
    if game is None:
        app.logger.warning(f'Invalid game ID: {game_id}')
        return flask.abort(404)
    state = flask.request.values.get('state')
    if state in license_plate_bingo.db.STATE_NAME_TO_ABBR:
        action = flask.request.values.get('action')
        found_states = game['found']
        if action == 'add':
            found_states.add(state)
            db.games_update(game_id, found_states)
        elif action == 'remove':
            found_states.discard(state)
            db.games_update(game_id, found_states)
        else:
            app.logger.warning(f'Invalid game update action: {action}')
    else:
        app.logger.warning(f'Invalid state: {state}')
    response = flask.make_response('', 204)
    response.headers['HX-Refresh'] = 'true'
    return response


@app.get('/new')
def new():
    game_id = get_db().games_insert()
    return flask.redirect(flask.url_for('play', game_id=game_id))


@app.get('/play/<uuid:game_id>')
def play(game_id: uuid.UUID):
    game = get_db().games_get(game_id)
    if game is None:
        return flask.abort(404)
    flask.g.game = game
    flask.g.state_name_to_abbr = license_plate_bingo.db.STATE_NAME_TO_ABBR
    return flask.render_template('play.html')


def main():
    app.logger.info(f'license-plate-bingo {__version__}')
    get_db().db_migrate()
    web_server_threads = int(os.getenv('WEB_SERVER_THREADS', 8))
    waitress.serve(app, ident=None, threads=web_server_threads)
