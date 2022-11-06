import flask
import waitress
import werkzeug.middleware.proxy_fix

__version__ = '2022.0'

app = flask.Flask(__name__)
app.wsgi_app = werkzeug.middleware.proxy_fix.ProxyFix(app.wsgi_app, x_port=1)


@app.before_request
def before_request():
    app.logger.debug(f'{flask.request.method} {flask.request.path}')
    flask.session.permanent = True
    flask.g.version = __version__


@app.get('/')
def index():
    return 'ok'


def main():
    app.logger.info(f'license-plate-bingo {__version__}')
    waitress.serve(app, ident=None)
