import flask
import license_plate_bingo.db
import os
import waitress
import werkzeug.middleware.proxy_fix

__version__ = '2022.0'

app = flask.Flask(__name__)
app.wsgi_app = werkzeug.middleware.proxy_fix.ProxyFix(app.wsgi_app, x_port=1)

db = license_plate_bingo.db.Database(os.getenv('DB'))


@app.before_request
def before_request():
    app.logger.debug(f'{flask.request.method} {flask.request.path}')
    # flask.session.permanent = True
    flask.g.version = __version__
    flask.g.debug_layout = True


@app.get('/')
def index():
    return flask.render_template('index.html')


@app.get('/play/game-id')
def play():
    flask.g.states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA',
        'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
        'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    ]
    return flask.render_template('play.html')


def main():
    app.logger.info(f'license-plate-bingo {__version__}')
    db.db_migrate()
    waitress.serve(app, ident=None)
