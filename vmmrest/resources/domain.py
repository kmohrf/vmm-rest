from http import HTTPStatus
from typing import MutableMapping

from flask_restful import fields as json_fields, marshal
from marshmallow import fields, Schema
import validators

from vmmrest.common import FlatNested, Quota, QuotaSchema, ServicesField, ServiceList
from vmmrest.resources import Resource
from vmmrest.util import create_body_parser, flatten, pick


class DomainSchema(Schema):
    note = fields.String()
    quota = fields.Nested(QuotaSchema)
    quota_propagate = fields.Boolean()
    services = ServicesField()
    services_propagate = fields.Boolean()
    transport = fields.String()
    transport_propagate = fields.Boolean()


class DomainCreateSchema(DomainSchema):
    name = fields.String(required=True, validate=validators.domain)


Domain = dict(
    name=json_fields.String(attribute='domain name'),
    gid=json_fields.Integer(),
    services=ServiceList(attribute='active services'),
    transport=json_fields.String(),
    quota=FlatNested(Quota),
    note=json_fields.String(),
    num_accounts=json_fields.Integer(attribute='accounts'),
    num_aliases=json_fields.Integer(attribute='aliases'),
    num_relocated=json_fields.Integer(attribute='relocated'),
    num_domain_catchalls=json_fields.Integer(attribute='catch-all dests'),
    num_domain_aliases=json_fields.Integer(attribute='alias domains')
)


class DomainBaseResource(Resource):
    def _dump_obj(self, name):
        return marshal(self.vmm.domain_info(name), Domain)

    def _save_to_obj(self, name, data: MutableMapping) -> None:
        for key, value in data.items():
            if key == 'note':
                self.vmm.domain_note(name, value)
            elif key == 'transport':
                propagate = data.get('transport_propagate', False)
                self.vmm.domain_transport(name, value, force=propagate)
            elif key == 'services':
                propagate = data.get('services_propagate', False)
                # TODO: domain_services signature is not python3-style.
                # this will fail with: got multiple values for argument 'force'
                self.vmm.domain_services(name, *value, force=propagate)
            elif key == 'quota':
                propagate = data.get('quota_propagate', False)
                num_messages, num_bytes = value.pop('num_messages'), value.pop('num_bytes')
                self.vmm.domain_quotalimit(name, num_bytes, num_messages, force=propagate)


class DomainCollectionResource(DomainBaseResource):
    parse_post = create_body_parser(DomainCreateSchema)

    def get(self):
        gids, gid_domains = self.vmm.domain_list()

        def _map(domains):
            return map(self._dump_obj, domains)
        return flatten(map(_map, gid_domains.values()))

    def post(self):
        data, errors = self.parse_post()
        name, transport, note = pick(data, ['name', 'transport', 'note'])
        self.vmm.domain_add(name, transport, note)
        self._save_to_obj(name, data)
        return self._dump_obj(name)


class DomainResource(DomainBaseResource):
    parse_put = create_body_parser(DomainSchema)

    def get(self, name):
        return self._dump_obj(name)

    def put(self, name):
        data, errors = self.parse_put()
        self._save_to_obj(name, data)
        return self._dump_obj(name)

    def delete(self, name):
        self.vmm.domain_delete(name, True, force=True)
        return '', HTTPStatus.NO_CONTENT


def register(app, api):
    api.add_resource(DomainCollectionResource, '/domains')
    api.add_resource(DomainResource, '/domains/<name>')
