from http import HTTPStatus

from flask import request
from flask_restful import fields as json_fields, marshal
from marshmallow import fields, Schema
from VirtualMailManager.constants import TYPE_ALIAS

from vmmrest.util import api_response, create_body_parser, flatten, pick
from vmmrest.resources import Resource


class AliasSchema(Schema):
    destinations = fields.List(fields.Email())


class AliasCreateSchema(AliasSchema):
    alias = fields.Email()


Alias = dict(
    address=json_fields.String(),
    destinations=json_fields.List(json_fields.String())
)


class AliasBaseResource(Resource):
    def _dump_obj(self, address):
        data = dict(
            address=address,
            destinations=list(self.vmm.alias_info(address))
        )
        return marshal(data, Alias)


class AliasCollectionResource(AliasBaseResource):
    parse_post = create_body_parser(AliasCreateSchema)

    @api_response('aliases')
    def get(self):
        pattern = request.args.get('pattern', None)
        # TODO: audit address_list if it’s safe against sql injections
        gids, gid_addresses = self.vmm.address_list(TYPE_ALIAS, pattern)

        def _map(address_infos):
            return map(lambda ai: self._dump_obj(ai[0]), address_infos)
        return flatten(map(_map, gid_addresses.values()))

    @api_response()
    def post(self):
        data, errors = self.parse_post()
        address, destinations = pick(data, ['address', 'destinations'])
        self.vmm.alias_add(address, *destinations)
        return self._dump_obj(address)


class AliasResource(AliasBaseResource):
    parse_put = create_body_parser(AliasSchema)

    @api_response()
    def get(self, address):
        return self._dump_obj(address)

    @api_response()
    def put(self, address):
        # put would be able to create new aliases but that wouldn’t be
        # pure doctrine so we’re going to check if the alias exists first
        self.vmm.alias_info(address)

        # alias_info would have thrown an exception, so we’re good to go
        data, errors = self.parse_put()
        self.vmm.alias_add(address, *data.pop('destinations'))
        return self._dump_obj(address)

    def delete(self, address):
        self.vmm.alias_delete(address)
        return '', HTTPStatus.NO_CONTENT


def register(app, api):
    api.add_resource(AliasCollectionResource, '/aliases')
    api.add_resource(AliasResource, '/aliases/<address>')
