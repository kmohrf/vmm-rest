from flask import Flask, g
from vmmrest.api import api_blueprint
from vmmrest.handler import RestHandler


__HANDLER = None

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/api')


if __name__ == '__main__':
    @app.before_first_request
    def _initialize_handler():
        global __HANDLER
        __HANDLER = RestHandler()

    @app.before_request
    def _add_handler_to_scope():
        g.handler = __HANDLER

    app.run()
