from flask import Blueprint
from flask_restful import Api
from logging import Logger

from .resources import register

logger = Logger(__name__)

api_blueprint = Blueprint('vmm_rest_api', __name__)
api = Api(api_blueprint)

register(api_blueprint, api)
