from flask import Flask, g
from vmmrest.api import api_blueprint
from vmmrest.handler import RestHandler

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/api')


@app.before_request
def _initialize_handler():
    g.handler = RestHandler()


if __name__ == '__main__':
    app.run()
