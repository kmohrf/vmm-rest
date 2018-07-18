from http import HTTPStatus

from flask_restful import fields as rfields, marshal
from marshmallow import Schema, fields, validate, UnmarshalResult
import validators
from VirtualMailManager.serviceset import SERVICES

from vmmrest.util import flatten, pick, create_body_parser
from vmmrest.resources import Resource


class ServiceList(rfields.Raw):
    def format(self, value):
        return value.split(' ')


class QuotaSchema(Schema):
    num_messages = fields.Integer(default=0)
    num_bytes = fields.Integer(default=0)


class DomainSchema(Schema):
    note = fields.String()
    quota = fields.Nested(QuotaSchema)
    quota_propagate = fields.Boolean()
    services = fields.List(fields.String(), validate=validate.ContainsOnly(SERVICES))
    services_propagate = fields.Boolean()
    transport = fields.String()
    transport_propagate = fields.Boolean()


class DomainCreateSchema(DomainSchema):
    name = fields.String(required=True, validate=validators.domain)


Quota = dict(
    num_messages=rfields.Integer(attribute='messages'),
    num_bytes=rfields.Integer(attribute='bytes')
)

Domain = dict(
    name=rfields.String(attribute='domain name'),
    gid=rfields.Integer(),
    services=ServiceList(attribute='active services'),
    transport=rfields.String(),
    quota=rfields.Nested(Quota),
    note=rfields.String(),
    num_accounts=rfields.Integer(attribute='accounts'),
    num_aliases=rfields.Integer(attribute='aliases'),
    num_relocated=rfields.Integer(attribute='relocated'),
    num_domain_catchalls=rfields.Integer(attribute='catch-all dests'),
    num_domain_aliases=rfields.Integer(attribute='alias domains')
)


class DomainBaseResource(Resource):
    def _dump_domain(self, name):
        return marshal(self.vmm.domain_info(name), Domain)

    def _save_to_domain(self, name, result: UnmarshalResult) -> None:
        data, errors = result

        for key, value in data.items():
            if key == 'note':
                self.vmm.domain_note(name, value)
            if key == 'transport':
                propagate = data.get('transport_propagate', False)
                self.vmm.domain_transport(name, value, force=propagate)
            if key == 'services':
                propagate = data.get('services_propagate', False)
                # TODO: domain_services signature is not python3-style.
                # this will fail with: got multiple values for argument 'force'
                self.vmm.domain_services(name, *value, force=propagate)
            if key == 'quota':
                propagate = data.get('quota_propagate', False)
                num_messages, num_bytes = value.pop('num_messages'), value.pop('num_bytes')
                self.vmm.domain_quotalimit(name, num_bytes, num_messages, force=propagate)


class DomainCollectionResource(DomainBaseResource):
    parse_post = create_body_parser(DomainCreateSchema)

    def get(self):
        gids, gid_domains = self.vmm.domain_list()

        def _map(domains):
            return map(self._dump_domain, domains)
        return flatten(map(_map, gid_domains.values()))

    def post(self):
        data = self.parse_post()
        name, transport, note = pick(data, ['name', 'transport', 'note'])
        self.vmm.domain_add(name, transport, note)
        self._save_to_domain(name, data)
        return self._dump_domain(name)


class DomainResource(DomainBaseResource):
    parse_put = create_body_parser(DomainSchema)

    def get(self, name):
        return self._dump_domain(name)

    def put(self, name):
        data = self.parse_put()
        self._save_to_domain(name, data)
        return self._dump_domain(name)

    def delete(self, name):
        self.vmm.domain_delete(name, True, force=True)
        return '', HTTPStatus.NO_CONTENT


def register(app, api):
    api.add_resource(DomainCollectionResource, '/domains')
    api.add_resource(DomainResource, '/domains/<name>')
