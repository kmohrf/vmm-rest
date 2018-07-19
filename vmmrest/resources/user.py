from http import HTTPStatus
from typing import MutableMapping

from flask_restful import fields as json_fields, marshal
from marshmallow import fields, Schema, validate
from VirtualMailManager.constants import TYPE_ACCOUNT
from VirtualMailManager.serviceset import SERVICES

from vmmrest.common import FlatNested, Quota, QuotaSchema, ServicesField
from vmmrest.util import assign, create_body_parser, flatten, pick
from vmmrest.resources import Resource


QuotaUsed = dict(
    num_messages_used=json_fields.Integer(attribute='uq_messages'),
    num_bytes_used=json_fields.Integer(attribute='uq_bytes'),
)


class PasswordSchemeField(fields.String):
    def __init__(self, **kwargs):
        def validator(value):
            from VirtualMailManager.password import list_schemes
            schemes, encodings = list_schemes()
            return validate.OneOf(list(schemes))(value)
        super().__init__(validate=validator, **kwargs)


class UserSchema(Schema):
    name = fields.String()
    note = fields.String()
    quota = fields.Nested(QuotaSchema)
    services = ServicesField()
    transport = fields.String()
    password = fields.String()
    password_scheme = PasswordSchemeField()


class UserCreateSchema(UserSchema):
    address = fields.Email(required=True)
    password = fields.String(required=True)


User = dict(
    address=json_fields.String(),
    name=json_fields.String(),
    uid=json_fields.Integer(),
    gid=json_fields.Integer(),
    services=json_fields.List(json_fields.String()),
    transport=json_fields.String(),
    quota=FlatNested(assign({}, Quota, QuotaUsed)),
    note=json_fields.String(),
)


class UserBaseResource(Resource):
    def _dump_user(self, address):
        info = self.vmm.user_info(address)
        info['services'] = []
        for service in SERVICES:
            if service in info and info[service].startswith('enabled'):
                info['services'].append(service)
        info['transport'] = info['transport'].replace(' [domain default]', '')
        return marshal(info, User)

    def _save_to_user(self, address, data: MutableMapping) -> None:
        for key, value in data.items():
            if key == 'name':
                self.vmm.user_name(address, value)
            elif key == 'password':
                scheme = data.pop('password_scheme', None)
                self.vmm.user_password(address, value, scheme)
            elif key == 'note':
                self.vmm.user_note(address, value)
            elif key == 'transport':
                # TODO: implement inherit from domain
                self.vmm.user_transport(address, value)
            elif key == 'services':
                # TODO: implement inherit from domain
                self.vmm.user_services(address, *value)
            elif key == 'quota':
                # TODO: implement inherit from domain
                num_messages, num_bytes = value.pop('num_messages'), value.pop('num_bytes')
                self.vmm.user_quotalimit(address, num_bytes, num_messages)


class UserCollectionResource(UserBaseResource):
    parse_post = create_body_parser(UserCreateSchema)

    def get(self):
        # TODO: add pattern support via query args
        gids, gid_addresses = self.vmm.address_list(TYPE_ACCOUNT)

        def _map(address_infos):
            return map(lambda ai: self._dump_user(ai[0]), address_infos)
        return flatten(map(_map, gid_addresses.values()))

    def post(self):
        data, errors = self.parse_post()
        address, password, note = pick(data, ['address', 'password', 'note'])
        self.vmm.user_add(address, password, note)
        self._save_to_user(address, data)
        return self._dump_user(address)


class UserResource(UserBaseResource):
    parse_put = create_body_parser(UserSchema)

    def get(self, address):
        return self._dump_user(address)

    def put(self, address):
        data, errors = self.parse_put()
        self._save_to_user(address, data)
        return self._dump_user(address)

    def delete(self, address):
        self.vmm.user_delete(address, True, force=True)
        return '', HTTPStatus.NO_CONTENT


def register(app, api):
    api.add_resource(UserCollectionResource, '/users')
    api.add_resource(UserResource, '/users/<address>')
