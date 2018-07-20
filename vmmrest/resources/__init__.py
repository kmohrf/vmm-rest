from flask import g
from flask_restful import Resource as _Resource
from VirtualMailManager import handler


class Resource(_Resource):
    @property
    def vmm(self) -> handler.Handler:
        return g.handler


def register(app, api):
    from . import aliases, domain, user
    for resource in [aliases, domain, user]:
        resource.register(app, api)
